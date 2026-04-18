\version "2.22.1"

\header {
  title = "081  God Will Take Care of You"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key bes \major
  \time 6/8
}

upper = {
  \global
  <<
    { \voiceOne d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf d''4 ees'8 e'8 c''8 f'8 bes'4. bes'8 c''8 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } f'4. a'8 g'8 ees'4 d'4. g'8 | d'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } d''4 ees'8 e'8 c''8 f'8 bes'4. bes'8 c''8 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } bes'2. a'8 g'8 f'4 c''8 | bes'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } g'4 f'8 a'4 f'4. g'8 | f'8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } ees'8 a'8 g'8 g'8 f'8 ees'4. d'4. | f'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } } } c''8 bes'8 c''8 bes'4 d''4. bes'8 | c''8^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "ii" } } } bes'2. bes'8 g'8 f'8 bes'8 a'8 | }
    { \voiceTwo bes2.\p | bes2. | bes2. | r2. | <d' ees'>2.\arpeggio | bes2. | <a bes d'>2.\arpeggio | r2. | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { bes,,8 } <f a c'>2.\p\arpeggio | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 f4 | \acciaccatura { bes,,8 } <f a c'>4\arpeggio a8 c'8 g4 | \acciaccatura { f,8 } <ees g bes>4\arpeggio g8 bes8 ees4 | \acciaccatura { ees,8 } <ees f a c'>4\arpeggio f8 a8 g4 | \acciaccatura { f,8 } <f a c'>4\arpeggio a8 c'8 c4 | \acciaccatura { bes,,8 } <bes, c ees g>4\arpeggio c8 ees8 d4 | \acciaccatura { c,8 } <c ees g>2.\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
