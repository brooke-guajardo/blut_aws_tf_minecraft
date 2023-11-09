FROM alpine:latest AS stage
WORKDIR /data
COPY MODS_NEED_DOWNLOAD.txt /data/MODS_NEED_DOWNLOAD.txt

FROM itzg/minecraft-server:java17-alpine
COPY --from=stage /data/MODS_NEED_DOWNLOAD.txt /data/MODS_NEED_DOWNLOAD.txt