#  Copyright (c) 2020. AV Connect Inc.
from unittest import TestCase
from data import models,db
from tests import test_utils


class TestDrivers(TestCase):
    def setUp(self) -> None:
        for driver in models.Driver.query().all():
            db.session.delete(driver)


    def tearDown(self) -> None:
        for driver in models.Driver.query().all():
            db.session.delete(driver)

    def test_clear(self):
        drivers = db.Driver.all()
        self.assertEqual(0, len(drivers))

        driver = db.Driver(name="fred")
        db.session.add(driver)
        db.session.commit()

        self.assertEqual(len(db.Driver.all()), 1)

    def test_clear2(self):
        drivers = db.Driver.all()
        self.assertEqual(0, len(drivers))

        driver = db.Driver(name="joe")
        db.session.add(driver)
        db.session.commit()

        self.assertEqual(len(db.Driver.all()), 1)