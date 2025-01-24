# Internship at Artifik (https://www.artifik.no)

## ETH Trading Bot with Reinforcement Learning

This project is the first part of my internship at **Artifik**, where I developed a cryptocurrency trading bot using reinforcement learning. The Actor-Critic using Kronecker-Factored Trust Region (ACKTR) algorithm was employed to predict ETH exchange prices. Pretrained models were utilized to evaluate market data and send orders.

### Key Features:
- A pretrained reinforcement learning model utilizing ACKTR predicts the next minute's ETH price and sends orders through the ALPACA API.
- The **model's accuracy** exceeds 50%, with **profits** close to 1%.
- **Gridbot** files are provided to showcase the bot's performance.

## ETH Trading Bot with RNN (LSTM)

This project is the second part of my internship at **Artifik**, where I developed a cryptocurrency trading bot using Recurrent Neural Networks (RNN), specifically Long Short-Term Memory (LSTM) networks. The model predicts ETH (Ethereum) prices based on their correlation with **Peruvian Sol (PEN)** and **Turkish Lira (TRY)** exchange rates.

### Key Features:
- **Peruvian Sol (PEN)** (Pearson Correlation = 0.82) and **Turkish Lira (TRY)** (Pearson Correlation = 0.71) are used as input features to predict ETH prices.
- The **model's accuracy** exceeds 80%, with **profits** close to 4%.
- **Final results**, including model performance and predictions, are available in the **Results** folder.