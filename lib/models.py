from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Create the database engine
engine = create_engine('sqlite:///freebies.db')
Base = declarative_base()

# Define the Company model
class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    founding_year = Column(Integer)
    freebies = relationship('Freebie', backref='company', cascade='all, delete-orphan')
    devs = relationship('Dev', secondary='freebies')

    def give_freebie(self, dev, item_name, value):
        new_freebie = Freebie(dev=dev, company=self, item_name=item_name, value=value)
        return new_freebie

    @classmethod
    def oldest_company(cls, session):
        return session.query(cls).order_by(cls.founding_year).first()

# Define the Dev model
class Dev(Base):
    __tablename__ = 'devs'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    freebies = relationship('Freebie', backref='dev', cascade='all, delete-orphan')
    companies = relationship('Company', secondary='freebies')

    def received_one(self, item_name):
        return any(freebie.item_name == item_name for freebie in self.freebies)

    def give_away(self, dev, freebie):
        if freebie.dev == self:
            freebie.dev = dev

# Define the Freebie model
class Freebie(Base):
    __tablename__ = 'freebies'

    id = Column(Integer, primary_key=True)
    dev_id = Column(Integer, ForeignKey('devs.id'))
    company_id = Column(Integer, ForeignKey('companies.id'))
    item_name = Column(String)
    value = Column(Integer)

    def print_details(self):
        return f"{self.dev.name} owns a {self.item_name} from {self.company.name}"

# Create the database tables
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Sample usage
if __name__ == "__main__":
    # Create some companies and devs
    company1 = Company(name="Company 1", founding_year=2000)
    company2 = Company(name="Company 2", founding_year=1995)
    dev1 = Dev(name="Dev 1")
    dev2 = Dev(name="Dev 2")

    # Give freebies
    company1.give_freebie(dev1, "T-shirt", 10)
    company2.give_freebie(dev1, "Sticker", 5)
    company2.give_freebie(dev2, "Keychain", 3)

    # Commit to the database
    session.add_all([company1, company2, dev1, dev2])
    session.commit()

    # Test aggregate methods
    print(dev1.received_one("T-shirt"))  # Should print True
    print(dev2.received_one("T-shirt"))  # Should print False

    dev1.give_away(dev2, dev1.freebies[0])
    session.commit()

    # Print freebie details
    for freebie in dev1.freebies:
        print(freebie.print_details())

    # Find the oldest company
    oldest_company = Company.oldest_company(session)
    print(f"The oldest company is {oldest_company.name} founded in {oldest_company.founding_year}")
