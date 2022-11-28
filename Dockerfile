FROM ubuntu:20.04
LABEL email="bonhyeon.gu@9bon.org"
LABEL name="BonhyeonGu"
VOLUME ["./appdata"]

WORKDIR /usr/src/app
RUN apt-get update
RUN apt-get install -y git wget p7zip p7zip-full
RUN apt-get install -y python3 python3-pip
RUN pip3 install flask youtube-transcript-api beautifulsoup4 lxml numpy nltk matplotlib networkx
RUN git clone https://github.com/BonhyeonGu/Reasoning_over_Knowledge_Component_Streams rk

WORKDIR /usr/src/app/rk
RUN wget https://github.com/BonhyeonGu/Reasoning_over_Knowledge_Component_Streams/releases/download/v1.0.0/anchorData.pkl
RUN wget https://github.com/BonhyeonGu/Reasoning_over_Knowledge_Component_Streams/releases/download/v1.0.0/ComIDToTitle.npy
RUN wget https://github.com/BonhyeonGu/Reasoning_over_Knowledge_Component_Streams/releases/download/v1.0.0/ComTittleToID.pkl
RUN wget https://github.com/BonhyeonGu/Reasoning_over_Knowledge_Component_Streams/releases/download/v1.0.0/backlinksZip.7z.001
RUN wget https://github.com/BonhyeonGu/Reasoning_over_Knowledge_Component_Streams/releases/download/v1.0.0/backlinksZip.7z.002
RUN 7z x backlinksZip.7z.001 -aoa
RUN rm backlinksZip.7z.001
RUN rm backlinksZip.7z.002
RUN mkdir pr0dens
RUN mkdir backlinks
RUN python3 unzipBacklinks.py
RUN python3 nltk_install.py

EXPOSE 5050
ENTRYPOINT [ "python3", "app.py" ]