import matplotlib.pyplot as plt
import pandas as pd
import numpy as np 

# Epochs
N = 50

# Arrange by block #
block_metrics = {key: {'loss': [], 'acc': []} for key in range(4, 16, 2)}
for block in range(4, 16, 2):
    df = pd.read_csv(f"../../xception_finetune_block{block}.csv")
    block_metrics[block]['acc'] = df['val_acc'].values.tolist()
    block_metrics[block]['loss'] = df['val_loss'].values.tolist()

# Could change I guess
plt.style.use("ggplot")

# Accuracy figure
plt.figure()

# Plot each accuracy
for block in block_metrics:
    plt.plot(np.arange(1, N+1), block_metrics[block]['acc'], label=f"block{block-1}_acc")
plt.title("Validation Accuracy on Dataset")
plt.xlabel("Epoch #")
plt.ylabel("Accuracy")
plt.legend(loc="lower left")
plt.savefig("finetune_acc_plot.png")


# Accuracy figure
plt.figure()

# Plot each accuracy
for block in block_metrics:
    plt.plot(np.arange(1, N+1), block_metrics[block]['loss'], label=f"block{block-1}_loss")
plt.title("Validation Loss on Dataset")
plt.xlabel("Epoch #")
plt.ylabel("Loss")
plt.legend(loc="lower left")
plt.savefig("finetune_loss_plot.png")



