import enum

"""
purpose: Enumaration class for all common used units of risk of collision.\n
"""
class SI_RISK_OF_COLLISION(enum.Enum):
  SI_RISK_OF_COLLISION = None

"""
purpose: Enumaration class for all common used units of mass.\n
"""
class SI_MASS(enum.Enum):
  SI_KILOGRAM = 1.0

  SI_GRAM = SI_KILOGRAM / 1000.0
  SI_METRIC_TON = 1000.0 * SI_KILOGRAM

"""
purpose: Enumaration class for all common used units of time.\n
"""
class SI_TIME(enum.Enum):
  SI_SECOND = 1.0

  SI_MINUTE = 60.0 * SI_SECOND
  SI_HOUR = 60.0 * 60.0 * SI_SECOND
  SI_DAY = 24.0 * 60.0 * 60.0 * SI_SECOND
  SI_WEEK = 7.0 * 24.0 * 60.0 * 60.0 * SI_SECOND
  SI_YEAR = 52.0 * 7.0 * 24.0 * 60.0 * 60.0 * SI_SECOND