import os
import csv
import sys
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement

from time import time
import datetime
import argparse

def ingestListings(datafile, session,consistency ):

    query = session.prepare('INSERT INTO mysimbdp.listings (id,  host_id , host_name,  neighbourhood ,latitude ,longitude, room_type , price , availability_365 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)')


    batch = BatchStatement(consistency_level=ConsistencyLevel.QUORUM)
    if(consistency =="ALL"):
        batch = BatchStatement(consistency_level=ConsistencyLevel.ALL)
    elif(consistency =="ONE") :
        batch = BatchStatement(consistency_level=ConsistencyLevel.ONE)
    
    with open(datafile) as csv_file:
        reader = csv.reader(csv_file, delimiter=',')
        next(csv_file)

        insertions=0
        for row in reader:
            try:
                id=int(row[0])
                host_id=int(row[1])
                host_name=row[2]
                neighbourhood=row[3]
                latitude=float(row[4])
                longitude=float(row[5])
                room_type=row[6]
                price=int(row[7])
                availability_365=int(row[8])
                batch.add(query,
                 (id,  host_id , host_name,  neighbourhood ,
                 latitude ,longitude,
                  room_type , price , availability_365 )
                  )
                
            except Exception as e:
                print('The cassandra error: {}'.format(e))
            try:
                session.execute(batch)
                batch.clear()              
                insertions+=1    
                if(insertions==200000): # to read only 200000 rows which is approx 20 mb
                    break 
                
            except Exception as e:
                print('The cassandra error: {}'.format(e))

           
    return insertions


if __name__ == "__main__":
    cluster = Cluster(['0.0.0.0'],port=9042)
    session = cluster.connect()

    datafile = sys.argv[1]
    consistency=sys.argv[2]
    start=time()
	insertions = ingestListings(datafile, session,consistency)

    stop=time()

    print("Inserted", insertions, "in", stop-start, "s", sep=" ")
