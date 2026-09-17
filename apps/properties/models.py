from django.conf import settings
from django.db import models


class Property(models.Model):
    STATUS_AVAILABLE = 'available'
    STATUS_RESERVED = 'reserved'
    STATUS_RENTED = 'rented'

    STATUS_CHOICES = (
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_RESERVED, 'Reserved'),
        (STATUS_RENTED, 'Rented'),
    )

    GOVERNORATE_NORTH_GAZA = 'north_gaza'
    GOVERNORATE_GAZA = 'gaza'
    GOVERNORATE_MIDDLE_GAZA = 'middle_gaza'
    GOVERNORATE_KHAN_YOUNIS = 'khan_younis'
    GOVERNORATE_RAFAH = 'rafah'

    GOVERNORATE_CHOICES = (
        (GOVERNORATE_NORTH_GAZA, 'شمال غزة'),
        (GOVERNORATE_GAZA, 'غزة'),
        (GOVERNORATE_MIDDLE_GAZA, 'وسط غزة'),
        (GOVERNORATE_KHAN_YOUNIS, 'خانيونس'),
        (GOVERNORATE_RAFAH, 'رفح'),
    )

    AREA_CHOICES = (
        # شمال غزة
        ('beit_lahia', 'بيت لاهيا'),
        ('umm_al_nasr', 'أم النصر'),
        ('jabalia_camp', 'مخيم جباليا'),
        ('jabalia', 'جباليا'),
        ('beit_hanoun', 'بيت حانون'),
        # غزة
        ('gaza_city', 'غزة'),
        ('shati_camp', 'الشاطئ'),
        ('mughraqa', 'المغراقة'),
        ('juhr_al_dik', 'جحر الديك'),
        ('zahra', 'مدينة الزهرة'),
        # وسط غزة
        ('masdar', 'المصدر'),
        ('nuseirat', 'النصيرات'),
        ('nuseirat_camp', 'مخيم النصيرات'),
        ('bureij', 'البريج'),
        ('zawayda', 'الزوايدة'),
        ('maghazi', 'المغازي'),
        ('maghazi_camp', 'مخيم المغازي'),
        ('wadi_salqa', 'وادي السلقا'),
        ('deir_al_balah_camp', 'مخيم دير البلح'),
        ('deir_al_balah', 'دير البلح'),
        # خانيونس
        ('qarara', 'القرارة'),
        ('khan_younis_city', 'خانيونس'),
        ('khan_younis_camp', 'مخيم خانيونس'),
        ('bani_suheila', 'بني سهيلا'),
        ('abasan_kabira', 'عبسان الكبيرة'),
        ('abasan_saghira', 'عبسان الصغيرة'),
        ('khuzaa', 'خزاعة'),
        ('fukhari', 'الفخاري'),
        # رفح
        ('rafah_city', 'رفح'),
        ('rafah_camp', 'مخيم رفح'),
        ('nasr', 'النصر'),
        ('shawka', 'الشوكة'),
    )

    AREA_TO_GOVERNORATE = {
        'beit_lahia': GOVERNORATE_NORTH_GAZA,
        'umm_al_nasr': GOVERNORATE_NORTH_GAZA,
        'jabalia_camp': GOVERNORATE_NORTH_GAZA,
        'jabalia': GOVERNORATE_NORTH_GAZA,
        'beit_hanoun': GOVERNORATE_NORTH_GAZA,
        'gaza_city': GOVERNORATE_GAZA,
        'shati_camp': GOVERNORATE_GAZA,
        'mughraqa': GOVERNORATE_GAZA,
        'juhr_al_dik': GOVERNORATE_GAZA,
        'zahra': GOVERNORATE_GAZA,
        'masdar': GOVERNORATE_MIDDLE_GAZA,
        'nuseirat': GOVERNORATE_MIDDLE_GAZA,
        'nuseirat_camp': GOVERNORATE_MIDDLE_GAZA,
        'bureij': GOVERNORATE_MIDDLE_GAZA,
        'zawayda': GOVERNORATE_MIDDLE_GAZA,
        'maghazi': GOVERNORATE_MIDDLE_GAZA,
        'maghazi_camp': GOVERNORATE_MIDDLE_GAZA,
        'wadi_salqa': GOVERNORATE_MIDDLE_GAZA,
        'deir_al_balah_camp': GOVERNORATE_MIDDLE_GAZA,
        'deir_al_balah': GOVERNORATE_MIDDLE_GAZA,
        'qarara': GOVERNORATE_KHAN_YOUNIS,
        'khan_younis_city': GOVERNORATE_KHAN_YOUNIS,
        'khan_younis_camp': GOVERNORATE_KHAN_YOUNIS,
        'bani_suheila': GOVERNORATE_KHAN_YOUNIS,
        'abasan_kabira': GOVERNORATE_KHAN_YOUNIS,
        'abasan_saghira': GOVERNORATE_KHAN_YOUNIS,
        'khuzaa': GOVERNORATE_KHAN_YOUNIS,
        'fukhari': GOVERNORATE_KHAN_YOUNIS,
        'rafah_city': GOVERNORATE_RAFAH,
        'rafah_camp': GOVERNORATE_RAFAH,
        'nasr': GOVERNORATE_RAFAH,
        'shawka': GOVERNORATE_RAFAH,
    }

    TYPE_APARTMENT = 'apartment'
    TYPE_VILLA = 'villa'
    TYPE_LAND = 'land'
    TYPE_STORE_ROOM = 'store_room'
    TYPE_SHOP = 'shop'
    TYPE_BARRACKS = 'barracks'

    PROPERTY_TYPE_CHOICES = (
        (TYPE_APARTMENT, 'شقة'),
        (TYPE_VILLA, 'فيلا'),
        (TYPE_LAND, 'قطعة أرض'),
        (TYPE_STORE_ROOM, 'حاصل'),
        (TYPE_SHOP, 'محل تجاري'),
        (TYPE_BARRACKS, 'بركس'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='properties',
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_AVAILABLE,
    )

    governorate = models.CharField(
        max_length=20,
        choices=GOVERNORATE_CHOICES,
        blank=True,
    )
    area = models.CharField(
        max_length=30,
        choices=AREA_CHOICES,
        blank=True,
    )
    neighborhood = models.CharField(max_length=255, blank=True)

    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPE_CHOICES,
        blank=True,
    )
    bedrooms = models.PositiveSmallIntegerField(null=True, blank=True)

    has_solar = models.BooleanField(default=False)
    has_generator_line = models.BooleanField(default=False)
    has_main_grid = models.BooleanField(default=False)
    has_water_tank = models.BooleanField(default=False)
    has_private_well = models.BooleanField(default=False)


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='images',
    )
    image = models.ImageField(upload_to='property_images/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.property.title}"

