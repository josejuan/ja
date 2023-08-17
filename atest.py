import torch
import nemo
import nemo.collections.asr as asr

MODEL_NAME='stt_es_quartznet15x5'

qn = asr.models.EncDecCTCModel.from_pretrained(model_name=MODEL_NAME) #.cuda()

for t in qn.transcribe(paths2audio_files=['../wavs/complex.wav']):
  print(f">>>> {t}")
