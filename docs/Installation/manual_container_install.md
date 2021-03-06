## Manual local jumpscaleX_core

If not installed already, install the docker software.  There is a lot of documentation on how to do this for your operating system.  Find more information about that [here](https://docs.docker.com/install/linux/docker-ce/binaries/)

Please check the installation by issuing the following commands:
```
docker image ls
docker ps
```

If this is successful you have a working docker environment! Now get yourself the latest (official) Ubuntu container:
```
docker pull ubuntu
```
This pulls in the office Ubuntu container from the docker hub and installs in onto your local system.  You can verify this by performing the following command:
```
docker image ls
```
The output should show that there is a ubuntu container installed on your local system.

We need to start this Ubuntu container. The rest of the installation will run inside the Ubuntu container. All of the modifications to the Ubuntu image will be stored inside the container.  This container will have the local installation of the jumpscale_coreX SDK.

Start the ubuntu container and login to a interactive (Unix) shell:
```
docker run -ti ubuntu
```
The result of this command is a Unix prompt, representing the ```root``` user account of the ubuntu system. For here onwards we will configure the container to be a local installation of the jumpscalecoreX SDK.

First update the Ubuntu binaries to the latest version:
```
apt update -y
```
Then add some additional software packages not part of the official container image:
```
apt install -y openssh-server locales curl git rsync unzip lsb python3 python3-pip
```
Then install a needed python package
```
pip3 install click
```
This is the complete update of the Ubuntu container to current patch levels. 

Now we start the installation the jumspcaleX_core SDK.  To do so we need an identity. We do this by configuring an RSA public and private key pair.
```
eval ssh-agent -s
```
This should return the process ID of the identity manger.  Then we create a public/private key pair
```
ssh-keygen
```
The binary will ask you where store the key pair - default answer is fine. It will then ask you to set a passphrase.  Just press enter twice or add an actual passphrase.

Next step is to get the public key added to the github account youown.  Look up your public key in on the chosen directory or of you opted for the default directory it should be this:
```
cd
cd .ssh
more id_rsa.pub
```
Copy the text and add it to you github account. Please find instructions here how to do this. Here is a manual how to do [this](https://help.github.com/en/articles/adding-a-new-ssh-key-to-your-github-account)

Once this is done - load the identity into your container root account:
```
ssh-add ~/.ssh/id_rsa
```
With the public key copied into the github account and the private key loaded in the container user account you now have access from the container to the github jumpscale repository.

Copy the install script to the local /tmp directory:
```
curl https://raw.githubusercontent.com/threefoldtech/jumpscaleX_core/master/install/jsx.py?$RANDOM > /tmp/jsx;
```
Make the install script executable:
```
chmod +x /tmp/jsx;
```
Set the correct terminal output environment variables:
```
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
```
And then run the install script to do a local install
```
/tmp/jsx install
```

Et presto, you have have a local installation of the jumpscaleX_core environment in your container. Test it out by starting the kosmos shell:
```
Source /sandbox/env.sh
Kosmos
```

Now that we've modified the container we have to commit the changes. First exit the container with the command exit. To commit the changes and create a new image based on said changes, issue the command:

When the container stops you are back the the terminal prompt on you laptop.  Find the container_id by executing the command:
```
docker image ls
```
With the optained container_id commit the new build container:
```
sudo docker commit CONTAINER_ID jumpscaleX_core
```
After this - anytime you want to restart the container use:
```
docker run -ti jumpscaleX_core
```

All done!
