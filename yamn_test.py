
from sqlalchemy import create_engine, MetaData
from sqlathanor import Table, AttributeConfiguration
from sqlathanor import declarative_base, as_declarative, Column
from sqlathanor import *
engine = create_engine('sqlite:///college.db', echo = True)

meta = MetaData()

my_table = Table.from_yaml('yaml_file.yaml', 
	'my_table_name', 
	meta,
	primary_key = 'id',
	)
	
print(my_table)

meta.create_all(engine)


my_table_name.update_from_yaml("fred.yaml")

