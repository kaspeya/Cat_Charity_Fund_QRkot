from sqlalchemy import Column, ForeignKey, Integer, Text

from .parent_donation_charityproject import DonationCharityProject


class Donation(DonationCharityProject):
    """ Модель для представления пожертвования в БД. """
    user_id = Column(Integer, ForeignKey('user.id'))
    comment = Column(Text)
