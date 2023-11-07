FROM ubuntu:latest AS stage
RUN apt-get update && apt-get install -y locales && rm -rf /var/lib/apt/lists/* \
	&& localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8
ENV LANG en_US.utf8
WORKDIR /app/
COPY helper.py helper.py
RUN python3 helper.py > /tmp/myvar
# extract secret 


FROM itzg/minecraft-server:latest
COPY --from=stage /tmp/myvar /tmp/myvar
RUN CF_API_KEY=$(cat /tmp/myvar)
ENV CF_API_KEY=$CF_API_KEY
RUN rm /tmp/myvar 