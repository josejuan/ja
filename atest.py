import nemo
import nemo.collections.asr as asr

# asr.models.EncDecCTCModel.list_available_models()

MODEL_NAME='stt_es_quartznet15x5'

qn = asr.models.EncDecCTCModel.from_pretrained(model_name=MODEL_NAME)
qn = qn.to('cuda')
for t in qn.transcribe(paths2audio_files=['../wavs/complex.wav']):
  print(f">>>> {t}")
