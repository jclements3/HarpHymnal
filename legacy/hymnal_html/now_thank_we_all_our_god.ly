\version "2.22.1"

\header {
  title = "176  Now Thank We All Our God"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key f \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } }\mf c''4 c''8 d''4 d''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } a'4 bes'4 \acciaccatura { bes'16 g'16 } a'4 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } f'4 e'4 f'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } c''4 c''8 d''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } c''4 a'4 \acciaccatura { c''16 a'16 } bes'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } g'4 f'4 e'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 g'4 g'8 a'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } g'4 g'4 \acciaccatura { bes'16 g'16 } a'4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 b'4 c''4 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''4 c''4 \acciaccatura { c''16 a'16 } bes'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 a'4 g'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" } } } f'4 e'4 \acciaccatura { g'16 e'16 } f'4 | }
    { \voiceTwo <e' f' a'>1\p\arpeggio | <bes d' f'>1\arpeggio | <g bes d'>1\arpeggio | <bes d' f'>1\arpeggio | <bes d' f'>1\arpeggio | c'1 | <f a c'>1\arpeggio | <f a c'>1\arpeggio | <f' a'>1\arpeggio | <f' a'>1\arpeggio | <g bes d'>1\arpeggio | <g a c'>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <f, a, bes, d>1\p\arpeggio | \acciaccatura { bes,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 g,4 | \acciaccatura { g,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 g,4 | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 c4 | \acciaccatura { bes,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 g,4 | \acciaccatura { g,,8 } <g, bes, d>4\arpeggio bes,8 d8 bes,8 d8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 g,4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 e8 g8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { f,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 a,4 | \acciaccatura { g,,8 } <g, bes, d f>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
