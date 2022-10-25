
# Definición de la clase Vector.
class V3(object):

  # Método constructor de la clase Vector.
  def __init__(self, x, y, z = 0, w = 0):
    self.x = x
    self.y = y
    self.z = z

  # Sobreescritura de la suma de vectores.
  def __add__(self, other):
    return V3((self.x + other.x), (self.y + other.y), (self.z + other.z))

  # Sobreescritura de la resta de vectores.
  def __sub__(self, other):
    return V3((self.x - other.x), (self.y - other.y), (self.z - other.z))

  # Sobreescritura de la multiplicación de vectores.
  def __mul__(self, other):

    # Si se multiplica un vector por un número real, el vector cambia sus dimensiones.
    if ((type(other) == int) or (type(other) == float)):
      return V3((other * self.x), (other * self.y), (other * self.z))

    # Si se multiplican dos vectores, se ejecuta un producto cruz.
    return V3(
      ((self.y * other.z) - (self.z * other.y)),
      ((self.z * other.x) - (self.x * other.z)),
      ((self.x * other.y) - (self.y * other.x)),
    )

  # Producto punto entre vectores.
  def __matmul__(self, other):
    return ((self.x * other.x) + (self.y * other.y) + (self.z * other.z))

  # Método que retorna la longitud de un vector.
  def length(self):
    return (((self.x ** 2) + (self.y ** 2) + (self.z ** 2)) ** 0.5)

  # Método que retorna el vector normalizado.
  def norm(self):
    return (self * (1 / self.length())) if (self.length() > 0) else V3(0, 0, 0)

  # Método que redondea las coordenadas del vector.
  def round_coords(self):
    self.x = round(self.x)
    self.y = round(self.y)
    self.z = round(self.z)

  # Representación en formato string del vector.
  def __repr__(self):
    return f"<{self.x}, {self.y}, {self.z}>"