from enum import Enum

class Letter:
    """
    Klasse zum Handling von Buchstaben in 2D-Koordinaten.
    Die Buchstaben sind als Tupel von Punkten definiert, wobei jeder Punkt ein Tupel aus x- und y-Koordinaten ist.
    Die Punkte werden später gerade verbunden, um die Form des Buchstabens zu zeichnen.
    Alle Buchstaben sind in einem Einheitsquadrat definiert, damit sie direkt in der Steuerung verwendet werden können.
    """
    def __init__(self, points: tuple[tuple[float, float], ...]):
        self.points = points

    def __len__(self):
        return len(self.points)

    def __str__(self) -> str:
        return "\n".join(
            f"Point(x={x}| y={y})" for x, y in self.points
        )



LETTER_A = Letter((
    (0.0, 0.0),
    (1.0, 0.3),
    (0.0, 0.6),
    (0.5, 0.45),
    (0.5, 0.18),
))

LETTER_B = Letter((
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 0.4),
    (0.75, 0.6),
    (0.5, 0.4),
    (0.5, 0.0),
    (0.5, 0.4),
    (0.25, 0.6),
    (0.0, 0.4),
    (0.0, 0.0)
))

LETTER_C = Letter((
    (0.0, 0.6),
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 0.6),
))

LETTER_D = Letter((
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 0.4),
    (0.5, 0.6),
    (0.0, 0.4),
    (0.0, 0.0),
))

LETTER_E = Letter(( # eventuell kurz abheben
    (0.0, 0.6),
    (0.0, 0.0),
    (0.5, 0.0),
    (0.5, 0.6),
    (0.5, 0.0),
    (1.0, 0.0),
    (1.0, 0.6)
))

LETTER_F = Letter(( # eventuell kurz abheben
    (0.0, 0.0),
    (0.5, 0.0),
    (0.5, 0.6),
    (0.5, 0.4),
    (1.0, 0.0),
    (1.0, 0.6)
))

LETTER_G = Letter((
    (0.4, 0.3),
    (0.4, 0.6),
    (0.0, 0.6),
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 0.6),
))

LETTER_H = Letter(( # eventuell kurz abheben
    (0.0, 0.0),
    (1.0, 0.0),
    (0.5, 0.0),
    (0.5, 0.6),
    (1.0, 0.6),
    (0.0, 0.6),
))

LETTER_I = Letter((
    (0.0, 0.3),
    (1.0, 0.3),
))

LETTER_J = Letter((
    (1.0, 0.3),
    (0.0, 0.3),
    (0.0, 0.0),
    (0.3, 0.0),
))

LETTER_K = Letter((
    (0.0, 0.0),
    (1.0, 0.0),
    (0.5, 0.0),
    (1.0, 0.6),
    (0.5, 0.0),
    (0.0, 0.6),
))

LETTER_L = Letter((
    (0.0, 0.6),
    (0.0, 0.0),
    (1.0, 0.0),
))

LETTER_M = Letter((
    (0.0, 0.0),
    (1.0, 0.0),
    (0.5, 0.3),
    (1.0, 0.6),
    (0.0, 0.6),
))

LETTER_N = Letter((
    (0.0, 0.0),
    (1.0, 0.0),
    (0.0, 0.6),
    (1.0, 0.6),
))

LETTER_O = Letter((
    (0.0, 0.2),
    (0.3, 0.0),
    (0.7, 0.0),
    (1.0, 0.2),
    (1.0, 0.4),
    (0.7, 0.6),
    (0.2, 0.3),
    (0.0, 0,4),
    (0.0, 0.2)
))

LETTER_P = Letter((
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 0.4),
    (0.75, 0.6),
    (0.5, 0.4),
    (0.5, 0.0)
))

LETTER_Q = Letter((
    (0.15, 0.5),
    (0.0, 0.4),
    (0.0, 0.2),
    (0.3, 0.0),
    (0.7, 0.0),
    (1.0, 0.2),
    (1.0, 0.4),
    (0.7, 0.6),
    (0.2, 0.3),
    (0.15, 0.5), # für (0.15, 0.5) -> (0.3, 0.4) eventuell kurz abheben
    (0.3, 0.4),
    (0.0, 0.6)
))

LETTER_R = Letter((
    (0.0, 0.0),
    (1.0, 0.0),
    (1.0, 0.4),
    (0.75, 0.6),
    (0.5, 0.4),
    (0.5, 0.0),
    (0.0, 0.6)
))

LETTER_S = Letter((
    (0.0, 0.0),
    (0.0, 0.3),
    (0.25, 0.5),
    (0.75, 0.0),
    (1.0, 0.3),
    (1.0, 0.6),
))

LETTER_T = Letter(( # besser abheben
    (0.0, 0.3),
    (1.0, 0.3),
    (1.0, 0.6),
    (1.0, 0.0),
))

LETTER_U = Letter((
    (1.0, 0.0),
    (0.2, 0.0),
    (0.0, 0.3),
    (0.2, 0.6),
    (1.0, 0.6),
))

LETTER_V = Letter((
    (1.0, 0.0),
    (0.0, 0.3),
    (1.0, 0.6),
))

LETTER_W = Letter((
    (1.0, 0.0),
    (0.0, 0.15),
    (0.6, 0.3),
    (0.0, 0.45),
    (1.0, 0.6),
))

LETTER_X = Letter(( #besser abheben
    (1.0, 0.0),
    (0.0, 0.6),
    (0.5, 0.3),
    (1.0, 0.6),
    (0.0, 0.0),
))

LETTER_Y = Letter((
    (1.0, 0.0),
    (0.5, 0.3),
    (1.0, 0.6),
    (0.5, 0.3),
    (0.0, 0.3),
))

LETTER_Z = Letter((
    (1.0, 0.0),
    (1.0, 0.6),
    (0.0, 0.0),
    (0.0, 0.6),
))

class DefaultLetters(Enum):
    """Zusammenfassung aller Buchstaben, die standardmäßig verwendet werden können. Alle Buchstaben sind in 2D-Koordinaten definiert, damit sie direkt in der Steuerung verwendet werden können."""
    LETTER_A = LETTER_A
    LETTER_B = LETTER_B
    LETTER_C = LETTER_C
    LETTER_D = LETTER_D
    LETTER_E = LETTER_E
    LETTER_F = LETTER_F
    LETTER_G = LETTER_G
    LETTER_H = LETTER_H
    LETTER_I = LETTER_I
    LETTER_J = LETTER_J
    LETTER_K = LETTER_K
    LETTER_L = LETTER_L
    LETTER_M = LETTER_M
    LETTER_N = LETTER_N
    LETTER_O = LETTER_O
    LETTER_P = LETTER_P
    LETTER_Q = LETTER_Q
    LETTER_R = LETTER_R
    LETTER_S = LETTER_S
    LETTER_T = LETTER_T
    LETTER_U = LETTER_U
    LETTER_V = LETTER_V
    LETTER_W = LETTER_W
    LETTER_X = LETTER_X
    LETTER_Y = LETTER_Y
    LETTER_Z = LETTER_Z

letter_dict = {
    'a': DefaultLetters.LETTER_A.value,
    'b': DefaultLetters.LETTER_B.value,
    'c': DefaultLetters.LETTER_C.value,
    'd': DefaultLetters.LETTER_D.value,
    'e': DefaultLetters.LETTER_E.value,
    'f': DefaultLetters.LETTER_F.value,
    'g': DefaultLetters.LETTER_G.value,
    'h': DefaultLetters.LETTER_H.value,
    'i': DefaultLetters.LETTER_I.value,
    'j': DefaultLetters.LETTER_J.value,
    'k': DefaultLetters.LETTER_K.value,
    'l': DefaultLetters.LETTER_L.value,
    'm': DefaultLetters.LETTER_M.value,
    'n': DefaultLetters.LETTER_N.value,
    'o': DefaultLetters.LETTER_O.value,
    'p': DefaultLetters.LETTER_P.value,    
    'q': DefaultLetters.LETTER_Q.value,
    'r': DefaultLetters.LETTER_R.value,
    's': DefaultLetters.LETTER_S.value,
    't': DefaultLetters.LETTER_T.value,
    'u': DefaultLetters.LETTER_U.value,
    'v': DefaultLetters.LETTER_V.value,
    'w': DefaultLetters.LETTER_W.value,
    'x': DefaultLetters.LETTER_X.value,
    'y': DefaultLetters.LETTER_Y.value,
    'z': DefaultLetters.LETTER_Z.value
}