import torch

if torch.cuda.is_available():
    print("GPU is available")
    device = torch.cuda.get_device_name(0)  # 0 represents the default GPU index
    print(f"Using GPU: {device}")
else:
    print("GPU is not available *************")
