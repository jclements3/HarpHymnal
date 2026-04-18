\version "2.22.1"

\header {
  title = "282  Were You There?"
  subtitle = "♩ = 80"
  tagline = ##f
}

global = {
  \key e \major
  \time 4/4
}

upper = {
  \global
  <<
    { \voiceOne b4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } }\mf e'4 gis'2 | gis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } gis'4 fis'4 e'4 | gis'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } fis'8 \acciaccatura { fis'16 dis'16 } e'2 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } gis'4 b'2 | b'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } b'4 cis''4 b'4 | b'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" } } } gis'8 fis'1 | \acciaccatura { cis''16 a'16 } b'2^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" "Δ" \raise #0.6 \smaller "2" } } } | e''4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } cis''8 b'1 | cis''4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } \acciaccatura { cis''16 a'16 } b'2 | gis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "I" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "2" } } } gis'4. fis'8 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } e'4 fis'4 e'2 | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } \acciaccatura { fis'16 dis'16 } e'2 | b4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "IV" } } } b2. | e'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "IV" "Δ" \raise #0.6 \smaller "3" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "V" "7" \raise #0.6 \smaller "3" } } } a'4 \acciaccatura { a'16 fis'16 } gis'2 | gis'4^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "V" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "iii" } } } gis'4 fis'4 e'4 | gis'4.^\markup { \override #'(baseline-skip . 1.8) \center-column { \with-color #(rgb-color 0.122 0.306 0.475) \concat { \bold "iii" } \with-color #(rgb-color 0.482 0.169 0.169) \concat { \bold "I" } } } fis'8 e'1 | r1 | }
    { \voiceTwo <e gis>1\p\arpeggio | <e gis b>1\arpeggio | <e gis b>1\arpeggio | r1 | <e' gis'>1\arpeggio | e'1 | <a b dis' fis'>1\arpeggio | a'1 | <a cis' e'>1\arpeggio | <dis e gis b>1\arpeggio | <gis a cis'>1\arpeggio | <gis a cis'>1\arpeggio | <b, dis fis>1\arpeggio | <gis a cis'>1\arpeggio | <b dis'>1\arpeggio | <gis b dis'>1\arpeggio | <a' cis'' e''>1\arpeggio | }
  >>
}

lower = {
  \clef bass
  \global
  \acciaccatura { b,,8 } <b, dis fis>1\p\arpeggio | \acciaccatura { e,8 } <b, dis fis>4\arpeggio dis8 fis8 dis8 fis8 cis4 | \acciaccatura { b,,8 } <b, dis fis>4\arpeggio dis8 fis8 dis8 fis8 b,4 | \acciaccatura { e,8 } <b, dis fis>4\arpeggio dis8 fis8 dis8 fis8 fis,4 | \acciaccatura { e,8 } <b, dis fis>4\arpeggio dis8 fis8 dis8 fis8 fis,4 | \acciaccatura { e,8 } <b, dis fis>4\arpeggio dis8 fis8 dis8 fis8 cis4 | \acciaccatura { b,,8 } <b, dis e gis>4\arpeggio dis8 e8 gis8 dis8 b,4 | \acciaccatura { e,8 } <e, gis, b,>4\arpeggio gis,8 b,8 gis,8 b,8 fis,4 | \acciaccatura { e,8 } <e, gis, b,>4\arpeggio gis,8 b,8 gis,8 b,8 e,4 | \acciaccatura { e,8 } <e, gis, a, cis>4\arpeggio gis,8 a,8 cis8 gis,8 b,4 | \acciaccatura { a,,8 } <a, b, dis fis>4\arpeggio b,8 dis8 fis8 b,8 b,4 | \acciaccatura { a,,8 } <a, b, dis fis>4\arpeggio b,8 dis8 fis8 b,8 a,4 | \acciaccatura { b,,8 } <a, cis e>4\arpeggio cis8 e8 cis8 e8 b,4 | \acciaccatura { a,,8 } <a, b, dis fis>4\arpeggio b,8 dis8 fis8 b,8 a,4 | \acciaccatura { b,,8 } <gis, b, dis>4\arpeggio b,8 dis8 b,8 dis8 a,4 | \acciaccatura { gis,,8 } <e, gis, b,>4\arpeggio gis,8 b,8 gis,8 b,8 fis,4 | \acciaccatura { e,8 } <e, gis, b,>1\arpeggio |
}

\score {
  \new PianoStaff <<
    \new Staff \upper
    \new Staff \lower
  >>
  \layout { }
  \midi { \tempo 4=80 }
}
