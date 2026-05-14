from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(
        max_length=80,
        blank=True,
        help_text="Nombre de icono Heroicons (ej: sparkles, beaker, sun)",
    )
    imagen = models.ImageField(upload_to="categorias/", blank=True, null=True)
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["orden", "nombre"]
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalogo:categoria", args=[self.slug])


class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    logo = models.ImageField(upload_to="marcas/", blank=True, null=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Marca"
        verbose_name_plural = "Marcas"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class Producto(models.Model):
    DISPONIBILIDAD_CHOICES = [
        ("en_stock", "En stock"),
        ("bajo_pedido", "Bajo pedido"),
        ("agotado", "Agotado"),
    ]

    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    sku = models.CharField(max_length=60, unique=True)
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name="productos"
    )
    marca = models.ForeignKey(
        Marca,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="productos",
    )
    descripcion_corta = models.CharField(max_length=300, blank=True)
    descripcion = models.TextField(blank=True)
    presentacion = models.CharField(
        max_length=120, blank=True, help_text="Ej: Galón 4L, Bolsa 25kg, Caja 12u"
    )
    imagen = models.ImageField(upload_to="productos/", blank=True, null=True)
    disponibilidad = models.CharField(
        max_length=20, choices=DISPONIBILIDAD_CHOICES, default="en_stock"
    )
    activo = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-destacado", "nombre"]
        indexes = [
            models.Index(fields=["activo", "destacado"]),
            models.Index(fields=["categoria", "activo"]),
        ]

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.nombre)
            slug = base
            i = 2
            while Producto.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("catalogo:detalle", args=[self.slug])

    @property
    def disponibilidad_color(self):
        return {
            "en_stock": "success",
            "bajo_pedido": "warning",
            "agotado": "error",
        }.get(self.disponibilidad, "neutral")


class ImagenProducto(models.Model):
    producto = models.ForeignKey(
        Producto, on_delete=models.CASCADE, related_name="imagenes"
    )
    imagen = models.ImageField(upload_to="productos/galeria/")
    orden = models.PositiveIntegerField(default=0)
    alt = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return f"Imagen {self.orden} de {self.producto.nombre}"
