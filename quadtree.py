import Image, ImageDraw

def avg_children(node):
    r = (node.nw.color.r + node.ne.color.r + node.sw.color.r + node.se.color.r)/4
    g = (node.nw.color.g + node.ne.color.g + node.sw.color.g + node.se.color.g)/4
    b = (node.nw.color.b + node.ne.color.b + node.sw.color.b + node.se.color.b)/4

    node.color = Color(r, g, b)

class Color():
    def __init__(self, r, g, b):
        self.r = r
        self.g = g
        self.b = b

class TreeNode():
    def __init__(self, color=None):
        self.color = color
        self.nw = None
        self.ne = None
        self.se = None
        self.sw = None

class QuadTree():
    def __init__(self, image):
        self.size = image.size[0]
        self.root = TreeNode()
        self.populate(image, self.root, 0, 0, self.size)

    def populate(self, image, node, x, y, size):
        if size == 1:
            pic = image.load()
            p = pic[x,y]
            node.color = Color(p[0], p[1], p[2])
        else:
            node.nw = TreeNode()
            node.ne = TreeNode()
            node.sw = TreeNode()
            node.se = TreeNode()

            self.populate(image, node.nw, x, y, size/2)
            self.populate(image, node.ne, x+size/2, y, size/2)
            self.populate(image, node.sw, x, y+size/2, size/2)
            self.populate(image, node.se, x+size/2, y+size/2, size/2)
            avg_children(node)

    def decompress(self):
        size = self.size
        img = Image.new('RGB', (size, size))
        if not self.root:
            return None
        draw = ImageDraw.Draw(img)
        for i in xrange(size):
            for j in xrange(size):
                c = self.get_pixel(i,j)
                draw.point([i,j], (c.r, c.g, c.b))
        return img

    def get_pixel(self, x, y):
        if not self.root or x > self.size or y > self.size or x < 0 or y < 0:
            return None
        return self._get_pixel(x, y, self.size, self.root)
    
    def _get_pixel(self, x, y, size, node):
        p = None
        if not node:
            return p
        if not node.nw:
            return node.color

        size /= 2

        if (x < size and y < size):
            return self._get_pixel(x, y, size, node.nw)
        if (x >= size and y < size):
            return self._get_pixel(x-size, y, size, node.ne)
        if (x < size and y >= size):
            return self._get_pixel(x, y-size, size, node.sw)
        if (x >= size and y >= size):
            return self._get_pixel(x-size, y-size, size, node.se)
        return p

    def prune(self, tol):
        if self.root:
            self._prune(self.root, tol)

    def _prune(self, node, tol):
        if node.nw:
            if self.check_prune(node, node, tol):
                node.nw = None
                node.ne = None
                node.sw = None
                node.se = None
            else:
                self._prune(node.nw, tol)
                self._prune(node.ne, tol)
                self._prune(node.sw, tol)
                self._prune(node.se, tol)

    def pixel_diff(self, a, b):
        return ((a.r-b.r)**2 + (a.g-b.g)**2 + (a.b-b.b)**2)

    def check_prune(self, parent, node, tol):
        nw, ne, sw, se = False, False, False, False
        if self.pixel_diff(parent.color, node.color) > tol:
            return False
        elif node.nw:
            nw = self.check_prune(parent, node.nw, tol)
            ne = self.check_prune(parent, node.ne, tol)
            sw = self.check_prune(parent, node.sw, tol)
            se = self.check_prune(parent, node.se, tol)
            return (nw and ne and sw and se)
        else:
            return True
        
            
        

image = Image.open('test2.png', 'r')
q = QuadTree(image)
q.prune(10000)
z = q.decompress()
z.save('result.png', 'PNG')
