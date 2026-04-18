\version "2.22.1"

\header {
  title = "064  Despair Not, O Heart"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \major
  \time 2/4
}

upper = {
  \global
  <<
    { \voiceOne f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } }\mf bes'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'8 \acciaccatura { bes'16 g'16 } a'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vii" "°" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'8 g'2 | \acciaccatura { g'16 e'16 } f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } } } | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "vi" } } } g'4 | a'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'8 \acciaccatura { d''16 bes'16 } c''4 | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'8 g'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4 | g'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'8 f'4 | e'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c'8 d'2 | c'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } \acciaccatura { e''16 c''16 } d''4 | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'8 c''4 | bes'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } a'8 g'2 | \acciaccatura { g'16 e'16 } f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "vi" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" } } } | }
    { \voiceTwo <g bes d'>2\p\arpeggio | <e g bes>2\arpeggio | <e g bes>2\arpeggio | <bes, c e g>2\arpeggio | <f a c'>2\arpeggio | f'2 | <c' e'>2\arpeggio | <d' f'>2\arpeggio | d'2 | <c' e'>2\arpeggio | <a, d f>2\arpeggio | <f a>2\arpeggio | <e' f' a'>2\arpeggio | <c' e' g'>2\arpeggio | <c' d' f'>2\arpeggio | <c d f a>2\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <f, a, c>2\p\arpeggio | \acciaccatura { g,,8 } <g, bes, d>2\arpeggio | \acciaccatura { e,8 } <c e g>2\arpeggio | \acciaccatura { c,8 } <c d f a>2\arpeggio | \acciaccatura { d,8 } <d f a>2\arpeggio | \acciaccatura { f,8 } <c e g>2\arpeggio | \acciaccatura { c,8 } <g, bes, d>2\arpeggio | \acciaccatura { g,,8 } <g, bes, d>2\arpeggio | \acciaccatura { d,8 } <g, bes, d>2\arpeggio | \acciaccatura { g,,8 } <g, bes, d>2\arpeggio | \acciaccatura { c,8 } <c e g>2\arpeggio | \acciaccatura { c,8 } <c e g>2\arpeggio | \acciaccatura { f,8 } <f, g, bes, d>2\arpeggio | \acciaccatura { g,,8 } <g, bes, d>2\arpeggio | \acciaccatura { c,8 } <c e g bes>2\arpeggio | \acciaccatura { c,8 } <c e g bes>2\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
