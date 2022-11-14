FROM node:alpine
WORKDIR /usr/src/app
RUN npm install -g ganache-cli
CMD ["ganache-cli", "-h", "0.0.0.0","-b","5","--secure","--account","0x67f549fdaf5e0173cb71fcc6dd66a19aac0e63c5a09acb287007dd98b0571f51,1000000000000000000000000000000000000000000000000"]
