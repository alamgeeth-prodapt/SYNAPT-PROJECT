import kagglehub

# Download latest version
path = kagglehub.dataset_download("likithagedipudi/supply-chain-disruption-and-recovery-dataset", output_dir="d/SYNAPT-PROJECT/")

print("Path to dataset files:", path)
