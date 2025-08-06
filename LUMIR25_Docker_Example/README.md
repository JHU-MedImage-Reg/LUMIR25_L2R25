# Test phase Docker submission examples and templates for LUMIR25 challenge

For detailed instructions, please visit: `learn2reg.grand-challenge.org/lumir-test-phase-submission/`. Please note that this webpage is accessible only to participants.
* `LUMIR25_Docker_Example/` contains the scripts we used to build a Docker container for VFA.

After placing the pretrained weights (see [here](https://github.com/JHU-MedImage-Reg/LUMIR25_L2R25/tree/main/LUMIR25_Docker_Example/pretrained_weights)), follow these steps:
* Run `bash build.sh` to build the Docker image for the VFA inference script. [[code](https://github.com/JHU-MedImage-Reg/LUMIR25_L2R25/blob/main/LUMIR25_Docker_Example/build.sh)]
* Run `bash export.sh` to export and save the Docker image as `reg_model.tar.gz`. [[code](https://github.com/JHU-MedImage-Reg/LUMIR25_L2R25/blob/main/LUMIR25_Docker_Example/export.sh)]
* Run `bash test.sh` to test the built Docker image on the validation dataset. [[code](https://github.com/JHU-MedImage-Reg/LUMIR25_L2R25/blob/main/LUMIR25_Docker_Example/test.sh)]
  * Make sure to update this section of the `test.sh` script: https://github.com/JHU-MedImage-Reg/LUMIR25_L2R25/blob/a11d1fa49f92b9c36795581b92e9240f13255e73/LUMIR25_Docker_Example/test.sh#L11-L13 according to the paths for the `.json` dataset file and the input and output directories.

Some useful commands to free your disk space if too many Docker images are built:\
`docker rmi -f $(docker images -aq) #delete all containers`\
`docker rm -vf $(docker ps -aq) #delete all containers including its volumes`\
`docker system prune #delete everything`
