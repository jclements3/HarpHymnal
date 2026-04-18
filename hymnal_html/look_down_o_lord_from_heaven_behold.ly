\version "2.22.1"

\header {
  title = "150  Look Down, O Lord, From Heaven Behold"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key d \minor
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } }\mf bes'4 a'4 g'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } d''4 bes'4 a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'4 a'4 \acciaccatura { a'16 f'16 } g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "2" } } } bes'4 a'4 g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "2" } } } bes'4 a'4 \acciaccatura { a'16 f'16 } g'4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } d''4 bes'4 a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'4 a'4 \acciaccatura { a'16 f'16 } g'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } bes'4 a'4 g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } a'4 f'4 \acciaccatura { f'16 d'16 } e'4 | d'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } f'4 g'4 a'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 bes'4 \acciaccatura { bes'16 g'16 } a'4 | bes'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } g'4 fis'4 g'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4 bes'4 c''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 bes'4 \acciaccatura { bes'16 g'16 } a'4 | }
    { \voiceTwo <bes d' f'>1\p\arpeggio | <bes d' f'>1\arpeggio | <bes d' f'>1\arpeggio | <a bes d' f'>1\arpeggio | <a bes d' f'>1\arpeggio | <bes d' f'>1\arpeggio | <bes d' f'>1\arpeggio | <c' d' f'>1\arpeggio | d'1 | bes1 | <bes d'>1\arpeggio | e'1 | e'1 | <e' g'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { d,8 } <e, g, bes,>1\p\arpeggio | \acciaccatura { d,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 e,4 | \acciaccatura { d,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 e,4 | \acciaccatura { g,,8 } <bes, d e g>4\arpeggio d8 e8 g8 d8 a,4 | \acciaccatura { g,,8 } <bes, d e g>4\arpeggio d8 e8 g8 d8 bes,4 | \acciaccatura { d,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 e,4 | \acciaccatura { d,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 e,4 | \acciaccatura { g,,8 } <d, e, g, bes,>4\arpeggio e,8 g,8 bes,8 e,8 g,4 | \acciaccatura { f,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 bes,4 | \acciaccatura { d,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 e,4 | \acciaccatura { d,8 } <e, g, bes,>4\arpeggio g,8 bes,8 g,8 bes,8 e,4 | \acciaccatura { g,,8 } <d, f, a,>4\arpeggio f,8 a,8 f,8 a,8 a,4 | \acciaccatura { g,,8 } <d, f, a,>4\arpeggio f,8 a,8 f,8 a,8 g,4 | \acciaccatura { f,8 } <d, f, a,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
