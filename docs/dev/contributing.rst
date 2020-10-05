.. _contributing:

Contributor's Guide
===================

If you're reading this, you're probably interested in contributing to Requests.
Thank you very much! Open source projects live-and-die based on the support
they receive from others, and the fact that you're even considering
contributing to the Requests project is *very* generous of you.

This document lays out guidelines and advice for contributing to this project.
If you're thinking of contributing, please start by reading this document and
getting a feel for how contributing to this project works. 
If you have any questions, feel free to reach out to either `Shailesh Gothi`_, `Shubham Londhe`_,
or `Srikar Chamala`_, the primary maintainers.

.. _Shailesh Gothi: https://github.com/srgothi92
.. _Shubham Londhe: https://github.com/LondheShubham153
.. _Srikar Chamala: https://github.com/srikarchamala

The guide is split into sections based on the type of contribution you're
thinking of making, with a section that covers general guidelines for all
contributors.

Be Cordial
----------

    **Be cordial or be on your way**. *—Shubham Londhe*

Requests has one very important rule governing all forms of contribution,
including reporting bugs or requesting features. This golden rule is
"`be cordial or be on your way`_".

**All contributions are welcome**, as long as
everyone involved is treated with respect.

.. _early-feedback:

Get Early Feedback
------------------

If you are contributing, do not feel the need to sit on your contribution until
it is perfectly polished and complete. It helps everyone involved for you to
seek feedback as early as you possibly can. Submitting an early, unfinished
version of your contribution for feedback in no way prejudices your chances of
getting that contribution accepted, and can save you from putting a lot of work
into a contribution that is not suitable for the project.

Contribution Suitability
------------------------

Our project maintainers have the last word on whether or not a contribution is
suitable for Requests. All contributions will be considered carefully, but from
time to time, contributions will be rejected because they do not suit the
current goals or needs of the project.

If your contribution is rejected, don't despair! As long as you followed these
guidelines, you will have a much better chance of getting your next
contribution accepted.


Code Contributions
------------------

Steps for Submitting Code
~~~~~~~~~~~~~~~~~~~~~~~~~

When contributing code, you'll want to follow this checklist:

1. Fork the repository on GitHub.
2. Write tests that demonstrate your bug or feature. Ensure that they fail.
3. Make your change.
4. Run the entire test suite again, confirming that all tests pass *including
   the ones you just added*.
5. Send a GitHub Pull Request to the main repository's ``master`` branch.
   GitHub Pull Requests are the expected method of code collaboration on this
   project.

The following sub-sections go into more detail on some of the points above.

Code Review
~~~~~~~~~~~

Contributions will not be merged until they've been code reviewed. You should
implement any code review feedback unless you strongly object to it. In the
event that you object to the code review feedback, you should make your case
clearly and calmly. If, after doing so, the feedback is judged to still apply,
you must either apply the feedback or withdraw your contribution.

New Contributors
~~~~~~~~~~~~~~~~

If you are new or relatively new to Open Source, welcome! vcf2fhir aims to
be a gentle introduction to the world of Open Source. If you're concerned about
how best to contribute, please consider mailing a maintainer (listed above) and
asking for help.

Please also check the :ref:`early-feedback` section.

python Developer's Code Style™
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The vcf2fhir codebase uses the `PEP 8`_ code style.

In addition to the standards outlined in PEP 8, we have a few guidelines:

- Line-length can exceed 79 characters, to 100, when convenient.
- Line-length can exceed 100 characters, when doing otherwise would be *terribly* inconvenient.
- Always use single-quoted strings (e.g. ``'#flatearth'``), unless a single-quote occurs within the string.

Additionally, one of the styles that PEP8 recommends for `line continuations`_
completely lacks all sense of taste, and is not to be permitted within
the Requests codebase::

    # Aligned with opening delimiter.
    foo = long_function_name(var_one, var_two,
                             var_three, var_four)

No. Just don't. Please. This is much better::

    foo = long_function_name(
        var_one,
        var_two,
        var_three,
        var_four,
    )

Docstrings are to follow the following syntaxes::

    def the_earth_is_flat():
        """NASA divided up the seas into thirty-three degrees."""
        pass

::

    def fibonacci_spiral_tool():
        """With my feet upon the ground I lose myself / between the sounds
        and open wide to suck it in. / I feel it move across my skin. / I'm
        reaching up and reaching out. / I'm reaching for the random or
        whatever will bewilder me. / Whatever will bewilder me. / And
        following our will and wind we may just go where no one's been. /
        We'll ride the spiral to the end and may just go where no one's
        been.

        Spiral out. Keep going...
        """
        pass

All functions, methods, and classes are to contain docstrings. Object data
model methods (e.g. ``__repr__``) are typically the exception to this rule.

Thanks for helping to make the world a better place!

.. _PEP 8: https://pep8.org/
.. _line continuations: https://www.python.org/dev/peps/pep-0008/#indentation

Documentation Contributions
---------------------------

Documentation improvements are always welcome! The documentation files live in
the ``docs/`` directory of the codebase. They're written in
`reStructuredText`_, and use `Sphinx`_ to generate the full suite of
documentation.

When contributing documentation, please do your best to follow the style of the
documentation files. This means a soft-limit of 79 characters wide in your text
files and a semi-formal, yet friendly and approachable, prose style.

When presenting Python code, use single-quoted strings (``'hello'`` instead of
``"hello"``).

.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _Sphinx: http://sphinx-doc.org/index.html


.. _bug-reports:

Bug Reports
-----------

Bug reports are hugely important! Before you raise one, though, please check
through the `GitHub issues`_, **both open and closed**, to confirm that the bug
hasn't been reported before. Duplicate bug reports are a huge drain on the time
of other contributors, and should be avoided as much as possible.

.. _GitHub issues: https://github.com/elimuinformatics/vcf2fhir/issues

