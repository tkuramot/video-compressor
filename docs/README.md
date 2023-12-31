# Video Compressor

## Table of Contents
1. [Description](#description)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)
5. [Demo](#demo)
6. [Technical details](#technical-details)
7. [References](#references)

## [Description](#description)
動画ファイルを圧縮したり、解像度を変更したり、アスペクト比を変更したり、音声に変換したり、指定した時間範囲でGIFに変換することができる。

## [Features](#features)
1. 圧縮
2. 解像度変更
3. アスペクト比を変更
4. 音声に変換
5. 指定した時間範囲でGIFに変換

## [Installation](#installation)
```bash
$ git clone https://github.com/tkuramot/video-compressor
$ cd video-compressor
$ make init
```

## [Usage](#usage)
```bash
$ make server
$ make client
```

## [Demo](#demo)
https://github.com/tkuramot/video-compressor/assets/106866329/5ad4b57d-9b31-42ad-bdfc-2999086219ef



## [Technical details](#technical-details)
###  protocol
header: 64 bytes
- JSON size: 16 bytes
- media type size: 1 byte
- payload size: 47 bytes

payload: arbitrary bytes
- JSON: 2^16 bytes at most
- medit type size: 1 ~ 4 bytes (mp4, mp3, json, avi, ...)
- payload size: 2^47 bytes at most

Request
```json
{
  // compress, resolutionChange, aspectRatioChange, audioExtract, gifConvert
  "operation": "compress",
  "params": {
    // required for compress
    "compressRate": "0.5",
    // required for aspectRatioChange
    "aspectRatio": "16:9",
    // required for resolutionChange 
    "resolution": "1280x720",
    // required for gifConvert
    "startSec": "12",
    "endSec": "25"
  }
}
```

Response
```json
{
  "status": 200,
  "message": "OK"
}
```

## [References](#references)
[ffmpeg-python](https://kkroening.github.io/ffmpeg-python/)
[ffmpeg](https://ffmpeg.org/ffmpeg.html)
[tkinter](https://docs.python.org/ja/3/library/tkinter.html)
http://www.nct9.ne.jp/m_hiroi/light/pytk01.html
