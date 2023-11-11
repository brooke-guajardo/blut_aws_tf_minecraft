FROM itzg/minecraft-server:java17-alpine
# Copy jar files of mods that won't auto download
VOLUME ["/data"]
WORKDIR /data
COPY *.jar /data/mods/*

# Copy old save file to use pregen world
VOLUME ["/worlds"]
WORKDIR /worlds
COPY DevOps_Yearn_for_the_Mines /worlds/DevOps_Yearn_for_the_Mines
