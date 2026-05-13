import pyxel
import math
import random

largeur, hauteur = 128, 128
taille_case = 16

chemin = [(127, 111), (104, 12), (104, 16), (72, 16), (72, 112), (40, 112), (40, 64), (0, 64)]
couleur_chemin = 12

liste_tours = []
liste_ennemis = []
liste_projectiles = []

coordonnees_tours = [(0, 0), (16, 0), (32, 0), (48, 0)]
sprites_ennemis = [(0, 0), (8, 0), (16, 0), (24, 0), (32, 0), (40, 0)]

stats_tours = [{"cout": 20, "degats": 1, "recharge": 16, "portee": 56, "couleur": 10, "contact": False}, {"cout": 35, "degats": 2, "recharge": 24, "portee": 64, "couleur": 9, "contact": False}, {"cout": 55, "degats": 4, "recharge": 36, "portee": 80, "couleur": 8, "contact": False}, {"cout": 80, "degats": 0, "recharge": 1, "portee": 0, "couleur": 11, "contact": True}]


def arrondir(n):
    return (n // taille_case) * taille_case


def rectangles_se_chevauchent(x1, y1, l1, h1, x2, y2, l2, h2):
    return not (x1 + l1 <= x2 or x2 + l2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1)


def est_sur_chemin(x, y):
    for dx, dy in [(2, 2), (8, 2), (13, 2), (2, 8), (8, 8), (13, 13)]:
        px = x + dx
        py = y + dy
        if 0 <= px < largeur and 0 <= py < hauteur:
            if pyxel.image(0).pget(px, py) == couleur_chemin:
                return True
    return False


class Curseur:
    def __init__(self):
        self.x = 16
        self.y = 16
        self.vitesse = 2

    def update(self):
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x += self.vitesse
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x -= self.vitesse
        if pyxel.btn(pyxel.KEY_UP):
            self.y -= self.vitesse
        if pyxel.btn(pyxel.KEY_DOWN):
            self.y += self.vitesse
        self.x = max(0, min(self.x, largeur - taille_case))
        self.y = max(0, min(self.y, hauteur - taille_case))

    def draw(self):
        x = arrondir(self.x)
        y = arrondir(self.y)
        pyxel.rectb(x, y, taille_case, taille_case, 11)
        pyxel.rectb(x + 1, y + 1, taille_case - 2, taille_case - 2, 7)


class Tour:
    def __init__(self, jeu, x, y, type_tour):
        self.jeu = jeu
        self.x = x
        self.y = y
        self.type_tour = type_tour
        self.u, self.v = coordonnees_tours[type_tour]
        self.largeur = 16
        self.hauteur = 16
        self.compteur = 0
        self.stats = stats_tours[type_tour]

    def update(self):
        if self.stats["contact"]:
            for ennemi in self.jeu.ennemis[:]:
                if not ennemi.mort and rectangles_se_chevauchent(self.x, self.y, 16, 16, ennemi.x, ennemi.y, 8, 8):
                    ennemi.mort = True
                    self.jeu.argent += 2 + ennemi.vie_max // 4
            return

        self.compteur += 1
        if self.compteur < self.stats["recharge"]:
            return

        cible = None
        distance_minimale = 10**9
        centre_x = self.x + 8
        centre_y = self.y + 8

        for ennemi in self.jeu.ennemis:
            if ennemi.mort:
                continue
            ex = ennemi.x + 4
            ey = ennemi.y + 4
            distance = (ex - centre_x) * (ex - centre_x) + (ey - centre_y) * (ey - centre_y)
            if distance < self.stats["portee"] * self.stats["portee"] and distance < distance_minimale:
                distance_minimale = distance
                cible = ennemi

        if cible is not None:
            self.jeu.projectiles.append(Projectile(self.jeu, self.x + 8, self.y + 8, cible, self.stats["degats"], self.stats["couleur"]))
            self.compteur = 0

    def draw(self):
        pyxel.blt(self.x, self.y, 1, self.u, self.v, self.largeur, self.hauteur, 0)


class Ennemi:
    def __init__(self, jeu):
        self.jeu = jeu
        self.index_chemin = 0
        self.x, self.y = chemin[0]
        self.vitesse = 1
        self.mort = False
        sprites_disponibles = sprites_ennemis[:min(jeu.vague, len(sprites_ennemis))]
        self.u, self.v = random.choice(sprites_disponibles)
        if jeu.vague < 3:
            self.vie_max = random.choice([4, 5, 6]) + jeu.vague
        else:
            if (self.u, self.v) in [(24, 0), (32, 0), (40, 0)]:
                self.vie_max = random.choice([8, 9, 10, 11]) + jeu.vague
            else:
                self.vie_max = random.choice([5, 6, 7, 8]) + jeu.vague // 2
        self.vie = self.vie_max

    def update(self):
        if self.mort:
            return False
        if self.index_chemin >= len(chemin) - 1:
            self.mort = True
            return False

        tx, ty = chemin[self.index_chemin + 1]

        if self.x < tx:
            self.x += self.vitesse
        elif self.x > tx:
            self.x -= self.vitesse
        elif self.y < ty:
            self.y += self.vitesse
        elif self.y > ty:
            self.y -= self.vitesse

        if self.x == tx and self.y == ty:
            self.index_chemin += 1

        return False

    def draw(self):
        pyxel.blt(self.x, self.y, 2, self.u, self.v, 8, 8, 0)


class Projectile:
    def __init__(self, jeu, x, y, cible, degats, couleur):
        self.jeu = jeu
        self.x = float(x)
        self.y = float(y)
        self.cible = cible
        self.degats = degats
        self.couleur = couleur
        dx = (cible.x + 4) - self.x
        dy = (cible.y + 4) - self.y
        distance = max(1.0, math.hypot(dx, dy))
        self.vx = dx / distance * 3.5
        self.vy = dy / distance * 3.5

    def update(self):
        if self.cible not in self.jeu.ennemis:
            return True

        self.x += self.vx
        self.y += self.vy

        cx = self.cible.x + 4
        cy = self.cible.y + 4

        if abs(self.x - cx) < 5 and abs(self.y - cy) < 5:
            if not self.cible.mort:
                self.cible.vie -= self.degats
                if self.cible.vie <= 0:
                    self.cible.mort = True
                    self.jeu.argent += 2 + self.cible.vie_max // 4
            return True

        if self.x < -8 or self.x > largeur + 8 or self.y < -8 or self.y > hauteur + 8:
            return True

        return False

    def draw(self):
        pyxel.circ(int(self.x), int(self.y), 2, self.couleur)


class Jeu:
    def __init__(self):
        pyxel.init(largeur, hauteur, title="Tower Defense")
        pyxel.load("theme.pyxres")
        self.reinitialiser()
        pyxel.run(self.update, self.draw)

    def reinitialiser(self):
        self.curseur = Curseur()
        self.tours = []
        self.ennemis = []
        self.projectiles = []
        self.argent = 80
        self.vague = 1
        self.compteur_spawn = 0
        self.nombre_spawn = 0
        self.nombre_a_spawn = 10 + self.vague * 4
        self.pause_vague = 0

    def poser_tour(self, type_tour):
        x = arrondir(self.curseur.x)
        y = arrondir(self.curseur.y)
        x = min(x, largeur - 16)
        y = min(y, hauteur - 16)
        cout = stats_tours[type_tour]["cout"]
        if self.argent < cout:
            return
        if type_tour != 3 and est_sur_chemin(x, y):
            return
        for tour in self.tours:
            if rectangles_se_chevauchent(x, y, 16, 16, tour.x, tour.y, 16, 16):
                return
        self.tours.append(Tour(self, x, y, type_tour))
        self.argent -= cout

    def spawn_ennemi(self):
        self.ennemis.append(Ennemi(self))

    def vague_suivante(self):
        self.vague += 1
        self.nombre_spawn = 0
        self.nombre_a_spawn = 10 + self.vague * 4
        self.compteur_spawn = 0
        self.pause_vague = 0

    def update(self):
        self.curseur.update()

        if pyxel.btnp(pyxel.KEY_J):
            self.poser_tour(0)
        if pyxel.btnp(pyxel.KEY_K):
            self.poser_tour(1)
        if pyxel.btnp(pyxel.KEY_L):
            self.poser_tour(2)
        if pyxel.btnp(pyxel.KEY_M):
            self.poser_tour(3)

        if self.nombre_spawn < self.nombre_a_spawn:
            self.compteur_spawn += 1
            delai = max(10, 45 - self.vague * 2)
            if self.compteur_spawn >= delai:
                self.spawn_ennemi()
                self.nombre_spawn += 1
                self.compteur_spawn = 0
        else:
            if len(self.ennemis) == 0:
                self.pause_vague += 1
                if self.pause_vague > 60:
                    self.vague_suivante()

        for ennemi in self.ennemis[:]:
            if ennemi.update():
                self.ennemis.remove(ennemi)

        for tour in self.tours:
            tour.update()

        for projectile in self.projectiles[:]:
            if projectile.update():
                self.projectiles.remove(projectile)

        self.ennemis[:] = [ennemi for ennemi in self.ennemis if not ennemi.mort]

    def draw(self):
        pyxel.cls(0)
        pyxel.blt(0, 0, 0, 0, 0, largeur, hauteur, 0)
        for tour in self.tours:
            tour.draw()
        for ennemi in self.ennemis:
            ennemi.draw()
        for projectile in self.projectiles:
            projectile.draw()
        self.curseur.draw()
        pyxel.text(2, 2, f"Argent:{self.argent}", 7)
        pyxel.text(2, 12, f"Vague:{self.vague}", 7)


Jeu()