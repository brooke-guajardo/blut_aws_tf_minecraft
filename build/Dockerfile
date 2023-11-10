FROM itzg/minecraft-server:java17-alpine
# Copy jar files of mods that won't auto download
COPY *.jar /data/mods/*
# Copy old save file to use pregen world
COPY DevOps_Yearn_for_the_Mines.zip /data/world/*