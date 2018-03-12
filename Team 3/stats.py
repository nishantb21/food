import pandas as pd

data = pd.read_csv('review.csv')

count = data.groupby(['userId']).size().reset_index(name = "counts")

def fn(df, reviews):
	a = []
	ids = df.userId

	for i in ids:
		dish_ids = data[data.userId == i]
		a.extend(dish_ids.dishId.tolist())

	b = set(a)
	print("Unique Dishes with", reviews, "Reviews per user", len(b))

uniqueUser = count.userId.unique()
print("Number of Unique User IDs", uniqueUser.shape)

c = count[count.counts == 1]
print("== 1 :",c.shape)

c5 = count[count.counts >= 5]
print(">= 5 :", c5.shape)

c7 = count[count.counts >= 7]
print(">= 7 :",c7.shape)

c10 = count[count.counts >= 10]
print(">= 10 :",c10.shape)

c20 = count[count.counts >= 20]
print(">= 20 :", c20.shape)

fn(c5, 5)
fn(c7, 7)
fn(c10, 10)

unique_5 = c5.userId

'''
print("Total Users >= 5 Reviews", len(unique_5))

totalReviews = 0

ones = 0
zeros = 0
usable = 0
for i in unique_5:
	temp = data[data.userId == i]
	totalReviews += temp.shape[0]
	o = temp[temp.rating >= 4].shape[0]
	z = temp[temp.rating < 4].shape[0]
	ones += o
	zeros += z 

	x = z / (o + z) * 100
	x = int(x)

	if x != 0 and x != 100:
		usable += 1

print("Total Reviews", totalReviews)

print("Total Positive Reviews", ones)
print("Total Negative Reviews", zeros)

print("Total Unbiased Reviews", usable)

'''
