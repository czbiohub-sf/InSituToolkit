from InSituToolkit.imaging_database import write_experiment
from starfish import Codebook

image_ids = ['ISP-2019-08-28-14-30-00-0001']
spot_channels = ['Cy5']
nuc_channel = ['DAPI']
stain_channels= ['FITC']
db_credentials = '/Users/kevin.yamauchi/Documents/db_credentials_new.json'
output_dir = "."

write_experiment(
    db_credentials, output_dir, image_ids,
    spot_channels=spot_channels, nuc_channels=nuc_channel, stain_channels=stain_channels,
    positions=[0, 1, 2, 3, 4, 5, 6]
)

codebook = [
      {
          Features.CODEWORD: [
              {Axes.ROUND.value: 0, Axes.CH.value: 0, Features.CODE_VALUE: 1},
          ],
          Features.TARGET: "Barcode"
      },
  ]

# instantiate and write the codebook
cb = Codebook.from_code_array(codebook)
codebook_path = './codebook.json'

cb.to_json(codebook_path)
