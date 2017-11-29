from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Category, Item, User

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# UserInfo
user1 = User(username="Nathan Drake", email="abc123@example.com", picture="http://vignette4.wikia.nocookie.net/uncharted/images/a/a8/DrakeU4RenderAvatar.png/revision/latest?cb=20141018162617")  # noqa
session.add(user1)
session.commit()


# Category: Action
category1 = Category(name="Action")
session.add(category1)
session.commit()

item1 = Item(name="Uncharted 4: A Thief's End", description="Drake, now retired from fortune hunting with his wife Elena, reunites with his estranged older brother Sam and longtime partner Sully to search for Captain Henry Avery's lost treasure.", picture="", category=category1, user=user1)  # noqa
session.add(item1)
session.commit()

item2 = Item(name="Nier: Automata", description="Set in the midst of a proxy war between machines created by otherworldly invaders and the remnants of humanity, the story follows the battles of a combat android, her companion, and a fugitive prototype.", picture="", category=category1, user=user1)  # noqa
session.add(item2)
session.commit()

item3 = Item(name="Resident Evil 7: biohazard", description="The story follows civilian Ethan Winters as he searches for his wife Mia, which leads him to a derelict plantation inhabited by the Baker family. Ethan must fight against the Baker family and a humanoid form of bacteria.", picture="", category=category1, user=user1)  # noqa
session.add(item3)
session.commit()

# Category: Casual
category2 = Category(name="Casual")
session.add(category2)
session.commit()


# Category: Fighting
category3 = Category(name="Fighting")
session.add(category3)
session.commit()

item4 = Item(name="Tekken 7", description="Set shortly after the events of Tekken 6, the plot focuses on the fights between martial artist Heihachi Mishima and his son, Kazuya.", picture="", category=category3, user=user1)  # noqa
session.add(item4)
session.commit()

item5 = Item(name="Street Fighter V", description="Street Fighter V carries on the side-scrolling fighting gameplay of its predecessors, in which two fighters use a variety of attacks and special abilities to knock out their opponent. ", picture="", category=category3, user=user1)  # noqa
session.add(item5)
session.commit()


# Category: Music & Party
category4 = Category(name="Music & Party")
session.add(category4)
session.commit()


# Category: Puzzle & Cards
category5 = Category(name="Puzzle & Cards")
session.add(category5)
session.commit()


# Category: Role Playing
category6 = Category(name="Role-Playing")
session.add(category6)
session.commit()

item6 = Item(name="Final Fantasy XV", description="Final Fantasy XV takes place on the fictional world of Eos. All the world's countries, bar the kingdom of Lucis, are under the dominion of the empire of Niflheim. Noctis Lucis Caelum, heir to the Lucian throne, goes on a quest to retake his homeland.", picture="", category=category6, user=user1)  # noqa

session.add(item6)
session.commit()

item7 = Item(name="Dragon Quest XI", description="Dragon Quest XI continues the gameplay of previous games in the series, in which players explore worlds and fight against various monsters, including the ability to explore high areas.", picture="", category=category6, user=user1)  # noqa

session.add(item7)
session.commit()

item8 = Item(name="Persona 5", description="The Phantom Thieves of Hearts explore the supernatural Metaverse realm to steal ill intent from the hearts of adults.", picture="", category=category6, user=user1)  # noqa

session.add(item8)
session.commit()

item9 = Item(name="Kingdom Hearts 2.5", description="ingdom Hearts HD 2.5 Remix includes Kingdom Hearts II Final Mix[7] and Kingdom Hearts Birth by Sleep Final Mix in high definition and with trophy support.", picture="", category=category6, user=user1)  # noqa

session.add(item9)
session.commit()


# Category: Shooter
category7 = Category(name="Shooter")
session.add(category7)
session.commit()

item10 = Item(name="Doom", description="Players take the role of an unnamed marine as he battles demonic forces from Hell that have been unleashed by the Union Aerospace Corporation on a future-set colonized planet Mars.", picture="", category=category7, user=user1)  # noqa

session.add(item10)
session.commit()

item11 = Item(name="Overwatch", description="Overwatch assigns players into two teams of six; each player selecting from a roster characters, known as heroes. Each hero has a unique style of play, whose roles are divided into four general categories: Offense, Defense, Tank, and Support. ", picture="", category=category7, user=user1)  # noqa

session.add(item11)
session.commit()


# Category: Simulation
category8 = Category(name="Simulation")
session.add(category8)
session.commit()


# Category: Sports
category9 = Category(name="Sports")
session.add(category9)
session.commit()


# Category: Strategy
category10 = Category(name="Strategy")
session.add(category10)
session.commit()


print "Items added!"
