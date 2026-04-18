\version "2.22.1"

\header {
  title = "046  By Grace I'm Saved"
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
    { \voiceOne c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf a'4 c''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "2" } } } c''4 bes'4 a'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { g'16 e'16 } f'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } g'4 f'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } bes'4 a'4 g'2 | c''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } a'4 \acciaccatura { d''16 bes'16 } c''4 | d''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "ii" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "2" } } } c''4 bes'4 a'4 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "viii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } \acciaccatura { g'16 e'16 } f'2 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } g'4 f'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } bes'4 a'4 g'2 | g'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } g'4 g'4 | a'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } c''4 c''4 \acciaccatura { cis''16 a'16 } b'4 | c''2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } c''4 a'4 | f'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } d''4 bes'4 a'2 | g'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "1" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "6" } } } f'1 | r1 | }
    { \voiceTwo f'1\p | <f' g'>1\arpeggio | <a d'>1\arpeggio | <a bes d'>1\arpeggio | <bes d' f'>1\arpeggio | f'1 | <f' g'>1\arpeggio | <a d'>1\arpeggio | <a bes d'>1\arpeggio | <a bes d' f'>1\arpeggio | <bes c' e'>1\arpeggio | f'1 | <c' e' g'>1\arpeggio | <bes d'>1\arpeggio | <e g bes c'>1\arpeggio | <bes' d'' f''>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { f,8 } <c e g>1\p\arpeggio | \acciaccatura { c,8 } <g, bes, c e>4\arpeggio bes,8 c8 e8 bes,8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { c,8 } <bes, c e g>4\arpeggio c8 e8 g8 c8 c4 | \acciaccatura { bes,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 g,4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { c,8 } <g, bes, c e>4\arpeggio bes,8 c8 e8 bes,8 d4 | \acciaccatura { c,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { c,8 } <bes, c e g>4\arpeggio c8 e8 g8 c8 c4 | \acciaccatura { bes,,8 } <bes, c e g>4\arpeggio c8 e8 g8 c8 d4 | \acciaccatura { c,8 } <c e f a>4\arpeggio e8 f8 a8 e8 g,4 | \acciaccatura { f,8 } <c e g>4\arpeggio e8 g8 e8 g8 c4 | \acciaccatura { c,8 } <bes, d f>4\arpeggio d8 f8 d8 f8 c4 | \acciaccatura { bes,,8 } <f, a, c>4\arpeggio a,8 c8 a,8 c8 g,4 | \acciaccatura { f,8 } <f, a, c d>4\arpeggio a,8 c8 d8 a,8 g,4 | \acciaccatura { f,8 } <f, a, c>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
