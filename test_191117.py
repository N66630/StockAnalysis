import pandas as pd
import matplotlib.pyplot as plt
date = pd.date_range('20180101', periods=6)
s = pd.Series([1,2,3,4,5,6], index=date)
# print (s)
# s.plot()
plt.plot(s)
plt.show()

#import matplotlib.pyplot as plt
#import numpy as np

#x = np.linspace(0, 20, 100)  # Create a list of evenly-spaced numbers over the range
#plt.plot(x, np.sin(x))       # Plot the sine of each x point
#plt.show()                   # Display the plot