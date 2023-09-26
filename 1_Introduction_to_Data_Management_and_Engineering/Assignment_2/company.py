from os import read
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy import Column, String  
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import Session
import pandas as pd
import sys
from requests import request


# Functions
def row2dict(row):
    """ function to return the session result into a dictionary
    INPUT: session.query().all() arg
    OUTPUT: dictionary mapping of the input
    """
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d

def results_to_df(dict_results):
    """ function to create a pd.DataFrame of a given dictionary and print the results
    INPUT: dictionary
    OUTPUT: None
    """
    for row in dict_results:
        data = row2dict(row)
        try:
            df = df.append(data, ignore_index=True)
        except:
            df = pd.DataFrame([data])
    try:
        print(df.to_string(index=False))
    except:
         print("No results found!")

def find_dealers(session,country):
    """ function to create a pd.DataFrame of a given dictionary and print the results
    INPUT: dictionary
    OUTPUT: None
    """
    ans = session.query(Dealer).filter_by(country=country).all()
    results_to_df(ans)

def select_entity():
    # ask user to select table
    print('\nSelect entity:')
    count = 0
    for table_name in base.metadata.tables:
        count += 1
        print(f"[{count}] {table_name}")
    entity =  input(f"Entity [1]-[{count}]: ")

    # Check if selection is valid and save to table_2
    while entity not in [str(i) for i in range(1, count+1)]:
        entity = input(f'\n\nWrong input!!! Entity should be between 1 and {count}: ')
    user_entiry = list(base.metadata.tables.keys())[int(entity)-1].capitalize()
    return user_entiry

def select_management():
    # ask user to select table
    print('\n(a) Insert entity\n\
(b) Delete entity\n\
(c) Entity update')
    selection_m =  input(f"\n\nSelect required action [a], [b] or [c]: ").lower()

    # Check if selection is valid and save to table_2
    while selection_m not in [l for l in 'abc']:
        selection_m = input(f'\n\nWrong input!!! Entity should be in (a,b,c): ')
    return   selection_m


if __name__ == '__main__':
    # Change password here
    db_string = "postgres://postgres:postgres@localhost:5432/company"

    db = create_engine(db_string)  
    base = declarative_base(db)
    Session = sessionmaker(db)  
    session = Session()

    # Create classes
    class Brand(base):
            __tablename__ = 'brand'
            __table_args__ = {'autoload': True}


    class Model(base):
            __tablename__ = 'model'
            __table_args__ = {'autoload': True} 


    class Options(base):
            __tablename__ = 'options'
            __table_args__ = {'autoload': True}


    class Customer(base):
            __tablename__ = 'customer'
            __table_args__ = {'autoload': True} 

    class Dealer(base):
            __tablename__ = 'dealer'
            __table_args__ = {'autoload': True}


    class Car(base):
            __tablename__ = 'car'
            __table_args__ = {'autoload': True}





    while True:
        print("""\nOptions:
        1) Entity management
        2) Entity Search
        3) Perform specific query (from question 2)""")
        selection = input("Select one of the above options [1], [2], [3]: ")

        while selection.strip() not in ('1','2','3'):
            print("""\nWrong input!!!\nSelect one of the following options [1], [2], [3]
        1) Entity management
        2) Entity Search
        3) Perform specific query (from question 2)""")
            selection = input("Select one of the above options [1], [2], [3]: ")

        selection = int(selection)

        # Entity management
        if selection == 1:
            table_1 = select_entity()
            print()
            sel_1 = select_management()

            if sel_1 == 'a' or sel_1 == 'b':
                if table_1.lower() == 'brand':
                    insert = input('Give Brand_name to insert/delete: ')

                    brand = Brand(brand_name=insert)
                    if sel_1 == 'a':
                        try:
                            session.add(brand)
                            session.commit()
                            print(f"{insert} successfully added to {table_1}")
                        except:
                            print(f'Not possible to add {insert} to {table_1}')
                    else:  
                        
                        found = session.query(Brand).filter_by(brand_name=insert).first()
                        session.delete(found)
                        try:
                            session.commit()
                            print(f"{insert} successfully deleted to {table_1}")
                        except:
                            print(f'Not possible to deleted {insert} from {table_1}')                    



                elif table_1.lower() == 'model':
                    insert = input('Give Brand_name, Model_Name to insert (separated with comma): ').split(',')
                    insert = [i.strip() for i in insert]
                    model = Model(brand_name=insert[0], model_name=insert[1])
                    if sel_1 == 'a':
                        try:
                            session.add(model)
                            session.commit()
                            print(f"{insert} successfully added to {table_1}")
                        except:
                            print(f'Not possible to add {insert} to {table_1}')
                    else:  
                        
                        found = session.query(Model).filter_by(brand_name=insert[0], model_name=insert[1]).first()
                        session.delete(found)
                        try:
                            session.commit()
                            print(f"{insert} successfully deleted to {table_1}")
                        except:
                            print(f'Not possible to deleted {insert} from {table_1}')                    


                elif table_1.lower() == 'options':
                    insert = input('Give Modelid, version, year, color, fuel, transmission to insert (separated with comma): ').split(',')
                    insert = [i.strip() for i in insert]
                    option = Options(modelid = insert[0], version=insert[1], year=insert[2], color=insert[3], fuel=insert[4], transmission=insert[4])
                    if sel_1 == 'a':
                        try:
                            session.add(option)
                            session.commit()
                            print(f"{insert} successfully added to {table_1}")
                        except:
                            print(f'Not possible to add {insert} to {table_1}')
                    else:  
                        
                        found = session.query(Options).filter_by(modelid = insert[0], version=insert[1], year=insert[2], color=insert[3], fuel=insert[4], transmission=insert[4]).first()
                        session.delete(found)
                        try:
                            session.commit()
                            print(f"{insert} successfully deleted to {table_1}")
                        except:
                            print(f'Not possible to deleted {insert} from {table_1}')     


                elif table_1.lower() == 'car':
                    insert = input('Give VIN, modelid, optionid to insert (separated with comma): ').split(',')
                    insert = [i.strip() for i in insert]
                    car = Car(vin = insert[0], modelid=insert[1], optionid=insert[2])
                    if sel_1 == 'a':
                        try:
                            session.add(car)
                            session.commit()
                            print(f"{insert} successfully added to {table_1}")
                        except:
                            print(f'Not possible to add {insert} to {table_1}')
                    else:  
                        
                        found = session.query(Options).filter_by(vin = insert[0], modelid=insert[1], optionid=insert[2]).first()
                        session.delete(found)
                        try:
                            session.commit()
                            print(f"{insert} successfully deleted to {table_1}")
                        except:
                            print(f'Not possible to deleted {insert} from {table_1}')     

            else:
                print('Update statements not suppoerted. Contact admin for support geo.chalkiopoulos@gmail.com.')
                



        # Entity Search
        elif selection == 2:
            table_2 = select_entity()
            print()
            # ask user to select field to filter
            count = 0
            col_names_2 = row2dict(session.query(globals()[table_2]).all()[0]).keys()
            for col in col_names_2:
                count += 1
                print(f"{count}) Search {table_2} using field: {col}")
            
            col_2_index = input(f"Choose a Field from 1 to {count}: ")
            # Check if selection is valid and save to col_2
            while col_2_index not in [str(i) for i in range(1, count+1)]:
                col_2_index = input(f'\n\nWrong input!!! Field should be between 1 and {count}:')
            col_2 = list(col_names_2)[int(col_2_index)-1]

            value = input(f'\n\nSelect the search term (ex. WV for brand): ')
            kwargs = {col_2 : value}
            ans = session.query(globals()[table_2]).filter_by(**kwargs).all()
            results_to_df(ans)


        # Perform specific query (from question 2)
        else:
            print("Select Query and selection serapated with comma (ex. 1, Polo)\n\
            [1] Select all models of specific Brand (specify brand)\n\
            [2] Select all options of specific model\n\
            [3] Select all cars of specific model\n\
            [4] Select all customers that own a specific model\n")
            num, field = input("Provide your selection (number, field). You May use % in case you want to fetch all results: ").split(',')
            field = field.strip()

            if num == '1':
                ans = session.query(Model).join(Brand).filter(Model.brand_name == Brand.brand_name, Model.brand_name.like(field))
                print(pd.read_sql(ans.statement,session.bind).to_string(index=False))

            elif num == '2':
                ans = session.query(Options).join(Model).filter(Model.modelid == Options.modelid, Model.model_name.like(field))
                print(pd.read_sql(ans.statement,session.bind).to_string(index=False))

            elif num == '3':
                ans = session.query(Car).join(Model).filter(Car.model_name == Model.model_name, Model.model_name.like(field))
                print(pd.read_sql(ans.statement,session.bind).to_string(index=False))

            elif num == '4':
                ans = session.query(Customer).join(Car).join(Model).filter(Customer.customerid == Car.customerid, Car.modelid == Model.modelid, Model.model_name.like(field))
                print(pd.read_sql(ans.statement,session.bind).to_string(index=False))
            else:
                print('Wrong selection, exiting.')



        stop = input("\n\nWould you like to exit (y/n)?  ")
        if stop.lower() == 'y':
            break





