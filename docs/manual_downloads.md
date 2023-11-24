# How to get list of Mods you need to manually download

## 1. Run image locally
```bash
docker run \
-e EULA=TRUE \
-e VERSION=1.20.1 \
-e TYPE=AUTO_CURSEFORGE \
-e CF_PAGE_URL="https://www.curseforge.com/minecraft/modpacks/all-the-mods-9" \
-e CF_API_KEY='your_cf_api_key' \
-e MEMORY=4G \
-d -p 25565:25565 --name mc itzg/minecraft-server:java17-alpine
```
Wait about a minute and it will fail because when curseforge auto download detects some of the mods failed to load, it'll return an exit code 1.

## 2. Check Failed Container Logs
Get the docker container ID
```bash
docker container ls -a
```
You should see results like
```bash
CONTAINER ID   IMAGE                                 COMMAND                  CREATED              STATUS                      PORTS     NAMES
ea6a48405d9f   itzg/minecraft-server:java17-alpine   "/start"                 About a minute ago   Exited (1) 27 seconds ago             minecraft

```
Grab the container ID, using the example above:

```bash
docker logs ea6a48405d9f -n 20
```
You should see a list of mods like so:
```bash
Some mod authors disallow automated downloads.
The following need to be manually downloaded into the repo or excluded:
(Also written to ./MODS_NEED_DOWNLOAD.txt)

Mod                          Filename                               Download page
===========================  =====================================  ====================================================================================
Industrial Foregoing         industrial-foregoing-1.20.1-3.5.9.jar  https://www.curseforge.com/minecraft/mc-mods/industrial-foregoing/files/4709710
FindMe                       findme-3.1.0-forge.jar                 https://www.curseforge.com/minecraft/mc-mods/findme/files/4614446
Dark Mode Everywhere         DarkModeEverywhere-1.20.1-1.2.2.jar    https://www.curseforge.com/minecraft/mc-mods/dark-mode-everywhere/files/4645933
Structory                    Structory 1.20.2 v1.3.3                https://www.curseforge.com/minecraft/mc-mods/structory/files/4767394
Functional Storage           functionalstorage-1.20.1-1.2.5.jar     https://www.curseforge.com/minecraft/mc-mods/functional-storage/files/4810615
Titanium                     titanium-1.20.1-3.8.23.jar             https://www.curseforge.com/minecraft/mc-mods/titanium/files/4810679
Refined Storage: Requestify  rsrequestify-1.20.1-2.3.3.jar          https://www.curseforge.com/minecraft/mc-mods/rs-requestify/files/4862132
Towers of the Wild Modded    totw_modded-1.0.2-1.20.1.jar           https://www.curseforge.com/minecraft/mc-mods/towers-of-the-wild-modded/files/4802113
All the Wizard Gear          allthewizardgear-1.20.1-1.0.8.jar      https://www.curseforge.com/minecraft/mc-mods/all-the-wizard-gear/files/4881868
[init] ERROR failed to auto-install CurseForge modpack

```
Use the links it gives and manually download from curse forge. These are the jar files needed for the dockerfile so it copies them into the image that will be used by the ECS.
And use the name that is in the URL to add to the env var in the ECS CF_EXCLUDE_MODS. This will make curseforge auto downlaod skip these mods and avoid the exit code 1. 