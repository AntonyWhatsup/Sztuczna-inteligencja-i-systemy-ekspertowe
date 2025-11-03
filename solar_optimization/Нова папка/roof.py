# roof.py
class Roof:
    """Model płaszczyzny dachu (Модель площини даху)."""
    def __init__(self, width, length):
        self.width = width   # Szerokość połaci (od kalenicy do krawędzi) (Ширина схилу (від гребеня до краю))
        self.length = length # Długość dachu (Довжина даху)