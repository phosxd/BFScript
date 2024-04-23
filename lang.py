class langC:
  class errorC:
    class stC:
      class condC:
        def __init__(s):
          s.diti = 'Direct int to int conditions are not yet supported. Conditions must be var to int or var to var.'
      def __init__(s):
        s.cond = s.condC()
    def __init__(s):
      s.st = s.stC()
  def __init__(s):
    s.error = s.errorC()

lang = langC()