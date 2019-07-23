#import matplotlib.pyplot as plt
import numpy as np
import importlib
import os
import sys

import imaging_db.filestorage.s3_storage as s3_storage
    
import imaging_db.utils.db_utils as db_utils
import imaging_db.filestorage.s3_storage as s3_storage
import imaging_db.database.db_operations as db_ops

class ImageDatabase:
	def __init__(self, credentials_filename):
		self.credentials_filename = db_utils.get_connection_str(credentials_filename)

	def getAcqMeta(self, dataset_identifier):
		importlib.reload(db_session)

		with db_ops.session_scope(self.credentials_filename) as session:
			# Find the Frames of interest
			all_frames = session.query(db_ops.Frames) \
			    .join(db_ops.FramesGlobal) \
			    .join(db_ops.DataSet) \
			    .filter(db_ops.DataSet.dataset_serial == dataset_identifier) \
				.all()

			acq_meta = all_frames[0].frames_global.metadata_json['IJMetadata']

		return acq_meta
	def getNbrPositions(self, dataset_identifier):
		importlib.reload(db_session)

		with db_ops.session_scope(self.credentials_filename) as session:
			# Find the Frames of interest
			frames_global = session.query(db_ops.FramesGlobal) \
			    .join(db_ops.DataSet) \
			    .filter(db_ops.DataSet.dataset_serial == dataset_identifier) \
				.all()

			nbr_positions = frames_global[0].nbr_positions


		return nbr_positions

	def getImageMeta(self, dataset_identifier):
		'''
			Return metadata for each frame in a list.

		'''

		importlib.reload(db_session)

		with db_ops.session_scope(self.credentials_filename) as session:
			datasets = session.query(db_ops.DataSet)
			
			# Find the Frames of interest
			all_frames = session.query(db_ops.Frames) \
				.join(db_ops.FramesGlobal) \
				.join(db_ops.DataSet) \
				.filter(db_ops.DataSet.dataset_serial == dataset_identifier) \
				.all()

			# Get the image metadata
			image_metadata = []
			for im in all_frames:
				image_metadata.append(im.metadata_json['MicroManagerMetadata'])

		return image_metadata

	def getFrames(self, dataset_identifier, channels='all', slices='all'):
		''' 
			Get particular slices from an imaging dataset.

			Todo: add slicing for pos and time.
		'''

		# Open the session
		importlib.reload(db_session)
		
		with db_ops.session_scope(self.credentials_filename) as session:
			datasets = session.query(db_ops.DataSet)
			
			# Find the Frames of interest
			all_frames = session.query(db_ops.Frames) \
				.join(db_ops.FramesGlobal) \
				.join(db_ops.DataSet) \
				.filter(db_ops.DataSet.dataset_serial == dataset_identifier)

			# Filter by channel
			if channels == 'all':
				pass

			elif type(channels) is tuple:
				slice_filtered = all_frames.filter(db_ops.Frames.channel_name.in_(channels))

			else:
				print('Invalid channel query')

			# Filter by slice
			if slices == 'all':
				pass

			elif type(slices) is tuple:
				slice_filtered = all_frames.filter(db_ops.Frames.slice_idx.in_(Frames))

			else:
				print('Invalid slice query')

			# Get the names of the files
			file_names = [im.filename for im in all_frames]
			# for im in all_frames:
			# 	file_names.append(im.file_name)

			# Get the bit depth 
			bit_depth = all_frames[0].frames_global.bit_depth

			# Get the shape of the stack
			# TODO: get the shape from the acq meta
			stack_shape = (
    			all_frames[0].frames_global.im_width,
    			all_frames[0].frames_global.im_height,
    			all_frames[0].frames_global.im_colors,
    			len(all_frames),
			)

			# Get the folder
			s3_dir = all_frames[0].frames_global.s3_dir

			# Download the files
			data_loader = s3_storage.DataStorage(s3_dir=s3_dir)
			im_stack = data_loader.get_stack(file_names, stack_shape, bit_depth)
			
		session.rollback()
		session.close()

		return im_stack

	def getStack(self, dataset_identifier, channel, time_idx=0, pos_idx=0, verbose=False):
		''' Download a stack at a given set of pos, time, channel indices

			Returns
			im_ordered : np.ndarray containing the image [time, chan, z, x, y]

		'''
		
		with db_ops.session_scope(self.credentials_filename) as session:
			datasets = session.query(db_ops.DataSet)
			
			# Find the Frames of interest
			all_frames = session.query(db_ops.Frames) \
				.join(db_ops.FramesGlobal) \
				.join(db_ops.DataSet) \
				.filter(db_ops.DataSet.dataset_serial == dataset_identifier) \
				.filter(db_ops.Frames.channel_name == channel) \
				.filter(db_ops.Frames.time_idx == time_idx) \
				.filter(db_ops.Frames.pos_idx == pos_idx) \
				.all()

			# Get the names of the files
			file_names = [im.file_name for im in all_frames]

			if len(file_names) == 0:
				raise ValueError('No images match query')

			# Get the bit depth 
			bit_depth = all_frames[0].frames_global.bit_depth

			# Get the shape of the stack
			# TODO: get the shape from the acq meta
			stack_shape = (
    			all_frames[0].frames_global.im_width,
    			all_frames[0].frames_global.im_height,
    			all_frames[0].frames_global.im_colors,
    			len(all_frames),
			)

			# Get the folder
			s3_dir = all_frames[0].frames_global.s3_dir

			# Download the files
			data_loader = s3_storage.DataStorage(s3_dir=s3_dir)
			im_stack = data_loader.get_stack(file_names, stack_shape, bit_depth)

			im_ordered = np.zeros((1, 1, stack_shape[3], stack_shape[0], stack_shape[1]), dtype='uint16')

			# Todo update get_stack so this isn't required...
			for im_idx in range(len(all_frames)):
				im_ordered[0, 0, im_idx, :, :] = im_stack[:, :, 0, im_idx]
			
		session.rollback()
		session.close()

		return im_ordered
