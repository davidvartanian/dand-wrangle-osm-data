# OpenStreetMap Project
## Data Wrangling with MongoDB
### David Vartanian

Map Area: Buenos Aires, Argentina

https://mapzen.com/data/metro-extracts/metro/buenos-aires_argentina/

## Problems encountered in the Map
### Street Type
I've noticed that normal street names in Argentina don't include *Calle* as part of their names, but other types do. For instance, *Avenida del Libertador* is an avenue. But, what is *Azcuénaga*? Well, it's a normal street. You can assume it because *Calle* is **always** omited.

### Numbers as street names
In general, streets in Argentina are named after former militar or political leaders, as well as country names, or even dates of important events. However, some cities use only numbers as street names. Others, though, use number and name. For instance, *43* (just the number) or *Avenida 13* (an avenue), or a more complex structure, *900 - General Juan Lavalle*.

### Complexity does not mean problem
After auditing all streets contained in *way* tags I could not find any technical problem. It seems that someone else have done this job before. Instead, there were many irregularities on street names contained in *node* tags. That's why I decided to audit both *nodes* and *ways*. Although it's been quite complex to identify street types from street names due to the different existent structures.

## Data Overview
### Basic statistical overview
The following information corresponds to the XML file *buenos-aires_argentina.osm* file downloaded from *MapZen Metro Extracts* website with size of 396MB, converted to a JSON file with size of 426MB.

#### MongoDB Import

```
➜  data git:(master) ✗ mongoimport -u openstreetmap -d openstreetmap -c buenosaires --file buenos-aires_argentina.json
Enter password:

2017-08-20T20:06:54.309+0200	connected to: localhost
2017-08-20T20:06:57.295+0200	[##......................] openstreetmap.buenosaires	47.0MB/426MB (11.0%)
2017-08-20T20:07:00.295+0200	[#####...................] openstreetmap.buenosaires	94.0MB/426MB (22.1%)
2017-08-20T20:07:03.295+0200	[########................] openstreetmap.buenosaires	148MB/426MB (34.7%)
2017-08-20T20:07:06.295+0200	[###########.............] openstreetmap.buenosaires	210MB/426MB (49.2%)
2017-08-20T20:07:09.295+0200	[##############..........] openstreetmap.buenosaires	264MB/426MB (61.9%)
2017-08-20T20:07:12.295+0200	[##################......] openstreetmap.buenosaires	322MB/426MB (75.6%)
2017-08-20T20:07:15.295+0200	[#####################...] openstreetmap.buenosaires	386MB/426MB (90.6%)
2017-08-20T20:07:17.214+0200	[########################] openstreetmap.buenosaires	426MB/426MB (100.0%)
2017-08-20T20:07:17.214+0200	imported 1891788 documents
```

#### Number of documents

```
> db.buenosaires.find().count()
1891788
```

#### Unique users
The total amount of unique users is *2677*, given by the following aggregation query:

```
> db.buenosaires.aggregate([
... {"$group": {"_id": "$created.uid"}},
... {"$group": {"_id": "unique_users", "count": {"$sum": 1}}}
... ])
{ "_id" : "unique_users", "count" : 2677 }
```

#### Number of nodes and ways
The total amount of nodes is *1553770*, and ways *337982*, given by the following aggregation query:

```
> db.buenosaires.aggregate([
... {"$match": {"$or": [{type:"node"},{type:"way"}]}},
... {"$group": {"_id": "$type", "count": {"$sum":1}}}
... ])
{ "_id" : "way", "count" : 337982 }
{ "_id" : "node", "count" : 1553770 }
```

#### Number of chosen type of nodes, like cafes, shops, etc.
Actually I wanted to know which are the most frequent *amenity* and *shop* nodes.

The following query reveals the Top 10 amenities:

```
db.buenosaires.aggregate([
... {"$match": {"$and": [{type:"node"}, {amenity: {"$ne": null}}]}},
... {"$group": {"_id": "$amenity", "count": {"$sum": 1}}},
... {"$sort": {"count": -1}},
... {"$limit": 10}
... ])
{ "_id" : "restaurant", "count" : 2841 }
{ "_id" : "pharmacy", "count" : 1557 }
{ "_id" : "school", "count" : 1182 }
{ "_id" : "bench", "count" : 1077 }
{ "_id" : "cafe", "count" : 1017 }
{ "_id" : "fast_food", "count" : 902 }
{ "_id" : "bank", "count" : 857 }
{ "_id" : "fuel", "count" : 817 }
{ "_id" : "parking", "count" : 600 }
{ "_id" : "ice_cream", "count" : 569 }
```

And this query reveals the Top 10 shops:

```
> db.buenosaires.aggregate([
... {"$match": {"$and": [{type: "node"}, {shop: {"$ne": null}}]}},
... {"$group": {"_id": "$shop", "count": {"$sum": 1}}},
... {"$sort": {"count": -1}},
... {"$limit": 10}
... ])
{ "_id" : "yes", "count" : 4302 }
{ "_id" : "clothes", "count" : 1404 }
{ "_id" : "convenience", "count" : 1123 }
{ "_id" : "supermarket", "count" : 1051 }
{ "_id" : "bakery", "count" : 783 }
{ "_id" : "butcher", "count" : 724 }
{ "_id" : "lottery", "count" : 682 }
{ "_id" : "hairdresser", "count" : 669 }
{ "_id" : "car_repair", "count" : 640 }
{ "_id" : "hardware", "count" : 541 }
```

Since the value *yes* is actually "*A shop of unspecified type*" as you can see [in TagInfo Documentation](https://taginfo.openstreetmap.org/keys/shop#values), let's try to get the shop type via amenity field:

```
> db.buenosaires.aggregate([
... {"$match": {"$and":[{type:"node"}, {shop:"yes"}]}},
... {"$project": {_id: 0, amenity: 1}},
... {"$group": {"_id": "$amenity", "count": {"$sum": 1}}}
... ])
{ "_id" : "taxi", "count" : 1 }
{ "_id" : "fuel", "count" : 41 }
{ "_id" : null, "count" : 4257 }
{ "_id" : "ice_cream", "count" : 2 }
{ "_id" : "events_venue", "count" : 1 }

```

Well, not really. There is a large amount of *shop: yes* documents without *amenity*. Let's see first whether it's worth to give a try to go further:

```
> db.buenosaires.aggregate([
... {"$match": {"$and":[{type:"node"}, {shop:"yes"}, {amenity:null, description:null, brand:null, craft:null}]}},
... {"$group": {"_id": "nodata", "count": {"$sum": 1}}}
... ])
{ "_id" : "nodata", "count" : 4227 }
```

After this result I decided not to go further looking for more information about shops with no description.


#### Top 3 contributing users

These are the most frequent users in this particular dataset:

```
> db.buenosaires.aggregate([
... {"$group": {"_id": "$created.user", "count": {"$sum": 1}}},
... {"$sort": {"count": -1}},
... {"$limit": 3}
... ])
{ "_id" : "Souchong", "count" : 235340 }
{ "_id" : "AgusQui", "count" : 179087 }
{ "_id" : "argenos", "count" : 157879 }
```


## Additional Ideas
I've spent some time trying to rank fields. Not including *pos*, *address* or *name*, what other fields could be useful to pay more attention to?

Since documents don't have a declared schema, it's common to find documents with different structure in the same collection. Running this map reduce command found [here](https://stackoverflow.com/a/2308036/3456290) in the MongoDB console I've found 764 possible keys, filtering by documents with type *node*:


```
> mr = db.runCommand({
... "mapreduce": "buenosaires",
... "map": function() {
...   if (this.type == 'node') {
...     for (var key in this) {
...       emit(key, null);
...     }
...   }
... },
... "reduce": function(key, data) { return null; },
... "out": "buenosaires_keys"
... })
{
	"result" : "buenosaires_keys",
	"timeMillis" : 17075,
	"counts" : {
		"input" : 1891788,
		"emit" : 8260422,
		"reduce" : 115110,
		"output" : 764
	},
	"ok" : 1
}
> db[mr.result].distinct("_id")
[
	"FIXME",
	"Game_ID",
	"ISO3166-1_alpha2",
	"_description_",
	"_id",
	"abandoned",
	...
	"wifi",
	"wikidata",
	"wikipedia"
]
```

Given the large amount of possible keys, it would be a better idea to filter those documents having only basic keys: [_id, type, id, pos, created]:

```
> db.buenosaires.find({"$where": "for (k in this) { if (this.type == 'node' && ['_id','type','id','pos','created'].indexOf(k)!==-1) { return false;}} return this;"}).count()
338018
```

Now I'm sure that almost 22% of documents are not eligible to be classified. I conclude this because it's not possible to classify an element based on its position, creation information or id. So some further action should be taken with these documents, like encouraging contributors to add more accurate information. Although this query is quite expensive, since it runs javascript code for each element in the loop.


## Conclusion
Street names in Argentina are complex due to omissions and the structure using only numbers, combined with names, or event dates. I spent some time creating a list to filter possible street names not referring to street types, what you can see in [audit.py](audit.py) file.