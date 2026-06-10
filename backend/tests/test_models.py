import pytest
from app import models


def test_customer_model_primary_key():
    pk_names = [c.name for c in models.Customer.__table__.primary_key]
    assert "id" in pk_names


def test_customer_unique_constraints():
    table = models.Customer.__table__
    uq_names = {c.name for c in table.constraints if getattr(c, 'name', None)}
    assert "uq_customer_org_phone" in uq_names
    assert "uq_customer_org_gst" in uq_names
