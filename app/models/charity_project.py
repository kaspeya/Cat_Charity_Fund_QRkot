from sqlalchemy import Column, String, Text

from .parent_donation_charityproject import DonationCharityProject


class CharityProject(DonationCharityProject):
    """ Модель для представления благотворительного проекта в БД. """
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
