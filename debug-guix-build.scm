#!/usr/bin/env -S guix shell guile -- guile -s
!#

(use-modules (ice-9 popen)
             (ice-9 rdelim)
             (ice-9 match)
             (srfi srfi-71))

;; (display "A\n")

(define (call-command-with-output cmd)
  ;; (display "B\n")
  (match-let* (((err . err-in) (pipe))
               (out (with-error-to-port err-in
                       (lambda _ (open-input-pipe cmd)))))
    #;(setvbuf err 'block
             (* 1024 1024 16))
    (values out err)))

(define (filter-port filter port)
  ;; (display "C\n")
  (while #t
    (let ((line (read-line port)))
      (cond ((eof-object? line)
             (close port)
             (break #t))
            ((filter line)
             (display "foo: ")
             (write line))))))

(define (call-with-filter filter cmd)
  ;; (display "D\n")
  (let* ((out err
          (call-command-with-output cmd)))
    (filter-port filter out)
    ;; (display "E\n")
    (filter-port filter err)
    ;; (display "F\n")
    ))

(define-public (test1)
(call-with-filter
 (lambda (line)
   ;; (display line)
   #t)
 "ls -lsa"))

(test1)
