# File: voter_analytics/models.py
# Author: Justin Liao (liaoju@bu.edu), 4/3/2025
# Description: define data models for the blog application 
from django.db import models

# Create your models here.
class Voter(models.Model):
    #model class that represents a voter in the database

    last_name = models.TextField()
    first_name = models.TextField()
    street_number = models.TextField()
    street_name = models.TextField()
    apartment_number = models.TextField()
    zip_code = models.TextField()


    dob = models.DateField()
    dor = models.DateField()

    party = models.CharField(max_length=2)
    precinct = models.CharField(max_length=2)
    
    v20state = models.BooleanField()
    v21town = models.BooleanField()
    v21primary = models.BooleanField()
    v22general = models.BooleanField()
    v23town = models.BooleanField()

    score = models.IntegerField()


    def __str__(self):
        '''Return a string representation of this model instance.'''
        return f'{self.first_name} {self.last_name} ({self.zip_code}, {self.party}), {self.score}'
    



def load_data():


    '''Function to load data records from CSV file into Django model instances.'''

    filename = '/Users/justi/Spring2025/412/newton_voters.csv'
    f = open(filename)
    f.readline() # discard headers
    Voter.objects.all().delete()

    for line in f:
        fields = line.split(',')
        print(fields)
        try:
            voter = Voter(last_name=fields[1],
                                first_name=fields[2],
                                street_number=fields[3],
                                street_name = fields[4],
                                apartment_number = fields[5],
                                zip_code = fields[6],
                                
                                dob = fields[7],
                                dor = fields[8],

                                party = fields[9],
                                precinct = fields[10],

                                v20state =  True if fields[11] == "TRUE" else False,
                                v21town = True if fields[12] == "TRUE" else False,
                                v21primary = True if fields[13] == "TRUE" else False,
                                v22general = True if fields[14] == "TRUE" else False,
                                v23town = True if fields[15] == "TRUE" else False,

                                score = fields[16],
                            )
            voter.save() # commit to database
            print(f'Created result: {voter}')
            
        except Exception as e:
            print(f"Skipped: {fields}")
            print(f"An error occurred: {e}")




    print(f'Done. Created {len(Voter.objects.all())} Results.')
