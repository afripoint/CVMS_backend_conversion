from django.db import models
import uuid
from django.utils.text import slugify


class Consignment(models.Model):
    SHIPMENT_STATUS = (
        ('cleared', 'Cleared'),
        ('in transit', 'In Transit'),
        ('delivered', 'Delivered'),
        ('incomplete', 'Incomplete'),
        ('in warehouse', 'In Warehouse'),
        ('payment pending', 'Payment Pending'),
        ('payment pending', 'Payment Pending'),
        ('awaiting inspection', 'Awaiting Inspection'),
    )
    PAYMENT_STATUS_CHOICE = (
        ('pending', 'Pending'),
        ('not paid', 'Not Paid'),
        ('paid', 'Paid'),
    )
    INSPECTION_STATUS_CHOICES = (
        ('done', 'Done'),
        ('not started', 'Not Started'),
        ('in progress', 'In Progress'),
    )
    bill_of_ladding = models.CharField(
        max_length=150, unique=True, blank=True, null=True
    )
    shipping_company = models.CharField(max_length=150, blank=True, null=True)
    consignee = models.CharField(max_length=150, blank=True, null=True)
    shipper = models.CharField(max_length=150, blank=True, null=True)
    container = models.CharField(max_length=150, blank=True, null=True)
    agency = models.CharField(max_length=50, blank=True, null=True)
    declarant = models.CharField(max_length=50, blank=True, null=True)
    shipped_on_board = models.DateField(blank=True, null=True)
    port_of_discharge = models.CharField(max_length=50, blank=True, null=True)
    port_of_load = models.CharField(max_length=150, blank=True, null=True)
    port_of_entry = models.CharField(max_length=150, blank=True, null=True)
    terminal = models.CharField(max_length=150, blank=True, null=True)
    bonded_terminal = models.CharField(max_length=150, blank=True, null=True)
    bonded_warehouse = models.CharField(max_length=150, blank=True, null=True)
    shipment_status = models.CharField(max_length=250, choices=SHIPMENT_STATUS, default='payment pending')
    description_of_goods = models.TextField(blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.CharField(max_length=50, blank=True, null=True)
    gross_weight = models.CharField(max_length=50, blank=True, null=True)
    eta = models.DateField(blank=True, null=True)
    vessel_voyage = models.CharField(max_length=150, blank=True, null=True)
    hs_code = models.CharField(max_length=250, blank=True, null=True)
    payment_status = models.CharField(max_length=250, default='pending')
    charges = models.CharField(max_length=50, blank=True, null=True)
    shipping_line = models.CharField(max_length=150, blank=True, null=True)
    inspection_status = models.CharField(max_length=150, choices=INSPECTION_STATUS_CHOICES, default='done')
    container_id = models.CharField(max_length=50, blank=True, null=True)
    slug = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.consignee

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.bill_of_ladding) + str(uuid.uuid4())

        super().save(*args, **kwargs)


# To generate the Tracking ID
class Tracker(models.Model):
    consignment = models.ForeignKey(
        Consignment, related_name="tracker", on_delete=models.CASCADE
    )
    tracking_id = models.CharField(max_length=150, unique=True, blank=True, null=True)
    slug = models.CharField(max_length=250, unique=True, blank=True, null=True)
    user_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.tracking_id} for {self.consignment.consignee}"

    def save(self, *args, **kwargs):

        if not self.slug:
            self.slug = slugify(self.consignment.bill_of_ladding) + str(uuid.uuid4())

        if not self.tracking_id:
            prefix = "CUST"
            unique_id = uuid.uuid4().hex[:6].upper()
            self.tracking_id = f"{prefix}-{unique_id}"

        super().save(*args, **kwargs)

       

class Stages(models.Model):
    SHIPMENT_STATUS = (
        ("in terminal", "In Terminal"),
        ("in warehouse", "In Warehouse"),
        ("undergoing inspection", "Undergoing Inspection"),
        ("payment", "Payment"),
        ("cleared", "Cleared"),
        ("in transit", "In Transit"),
    )
    tracker = models.ForeignKey(
        Tracker, related_name="stages", on_delete=models.CASCADE
    )
    shipping_status = models.CharField(
        max_length=50, choices=SHIPMENT_STATUS, default="in transit"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment status of the {self.tracker.consignment.consignee} with {self.tracker.tracking_id}"


class TrackingRecord(models.Model):
    TRACKING_STATUS = (
        ("tracking created", "Tracking Created"),
        ("tracking updated", "Tracking Updated"),
    )
    created_by = models.ForeignKey(
        Consignment, related_name="consignment", on_delete=models.CASCADE
    )
    updated_by = models.CharField(max_length=50, blank=True, null=True)
    tracking_status = models.CharField(
        max_length=50, choices=TRACKING_STATUS, default="tracking created"
    )
    slug = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.created_by.consignee

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.created_by.bill_of_ladding) + str(uuid.uuid4())

        super().save(*args, **kwargs)


class SearchHistory(models.Model):
    consignment = models.ForeignKey(Consignment, on_delete=models.CASCADE)
    stages = models.ForeignKey(Stages, on_delete=models.CASCADE)
    tracker = models.ForeignKey(Tracker, on_delete=models.CASCADE)
    slug = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"search history for {self.consignment.bill_of_ladding}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.consignment.bill_of_ladding) + str(uuid.uuid4())
        super().save(*args, **kwargs)
