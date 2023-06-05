# Deanonymization: Music Listening Activity

This projects attempts to deanonymize the last.fm dataset, which includes 92,800 artist listening records from 1892 users (https://grouplens.org/datasets/hetrec-2011/). This deanonymizes the last.fm dataset by matching the pseudonymous user IDs with the names on a non-anonymous music website (https://aifairness.tech/) using a similarity function. 

Note: the non-anonymous music website only includes first names of users and their listening activity (artist and number of times listened to a song), so while this project deanonymizes the last.fm dataset, it only matches a user id with the first names of a user.

Created by: Kathy Yao
