FROM itzg/minecraft-server:java17-alpine
# Copy jar files of mods that won't auto download
VOLUME ["/data"]
WORKDIR /data
COPY *.jar /data/mods/*