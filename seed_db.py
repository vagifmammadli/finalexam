"""
Database Seeding Script
Populates the database with subjects and questions
"""
from app import app, db, Subject, Question


def seed_database():
    """Seed the database with default subjects and questions"""
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        print("Baza təmizləndi.")

        # Create subjects
        subj_arch = Subject(name="Kompüter Arxitekturası")
        subj_math = Subject(name="Riyazi Analiz")

        db.session.add(subj_arch)
        db.session.add(subj_math)
        db.session.commit()

        # ==========================================
        # RİYAZİ ANALİZ SUALLARI
        # ==========================================
        
        # Easy Questions (Q1-Q23: Çoxluqlar, Limitlər, Kəsilməzlik)
        math_easy = [
            (r"1. Prove the equality \(A \cap B = B \cap A\) (Theoretical)", "Easy"),
            (r"2. Prove that a non-empty set of numbers that is bounded above has an upper bound. (Theoretical)", "Easy"),
            (r"3. Prove that a non-empty numerical set bounded below has a lower bound. (Theoretical)", "Easy"),
            (r"4. If \(\{x\}\) is a set of numbers and \(\{-x\}\) is the set of negatives, prove \(\inf\{-x\} = -\sup\{x\}\).", "Easy"),
            (r"5. Find the domain of \(f(x)=7\cot(\pi x)+\arcsin(18^{x})\)", "Easy"),
            (r"6. Find the range of \(f(x)=\sqrt{-4x^{2}+8x+5}\)", "Easy"),
            (r"7. Prove the uniqueness of the limit of a convergent sequence. (Theoretical)", "Easy"),
            (r"8. Prove that a convergent numerical sequence is bounded. (Theoretical)", "Easy"),
            (r"9. Prove the Squeeze Theorem: If \(x_{n}\le y_{n}\le z_{n}\) and limits match, then \(y_n\) converges. (Theoretical)", "Easy"),
            (r"10. Prove \(x_{n}=\frac{16n}{5n^{3}+6}\) is infinitesimal.", "Easy"),
            (r"11. Prove \(x_{n}=\frac{5n}{2^{n}}\) is infinitesimal.", "Easy"),
            (r"12. Prove that an increasing and bounded-above numerical sequence is convergent. (Theoretical)", "Easy"),
            (r"13. Cauchy criterion for convergence: A sequence is convergent iff it is a Cauchy sequence. (Theoretical)", "Easy"),
            (r"14. Prove \(x_{n}=\sum_{k=1}^{n}\frac{\sin k}{5^{k}}\) is Cauchy convergent.", "Easy"),
            (r"15. Prove that the limit of \(f(x)=\sin\frac{1}{x}\) is not infinity as \(x\rightarrow0\).", "Easy"),
            (r"16. Determine limits of \(f(x)=4\arctan(\frac{16}{9x+2})\) as \(x\to 0\).", "Easy"),
            (r"17. Prove that \(\lim_{x\rightarrow0}\frac{\sin x}{x}=1\). (Theoretical)", "Easy"),
            (r"18. Find \(a, b\) for \(\lim_{x\rightarrow\infty}(\frac{x^{2}+2}{x+1}-5ax-9b)=0\).", "Easy"),
            (r"19. Determine the discontinuity point and its type for \(f(x)=\frac{|x-21|}{x-21}\).", "Easy"),
            (r"20. Investigate the continuity of \(f(x)=|x-5|\).", "Easy"),
            (r"21. Prove that \(f(x)=\frac{1}{x}\) is continuous at any point of its domain.", "Easy"),
            (r"22. Investigate the continuity of \(f(x)=\sin(\frac{1}{3x})\) for \(x\ne0, f(0)=0.5\).", "Easy"),
            (r"23. Investigate the continuity of \(f(x)=\begin{cases}\frac{x^{2}-16}{x-4},&x\ne4\\ 2a+1,&x=4\end{cases}\) at \(x=4\).", "Easy")
        ]

        # Medium Questions (Q24-Q54: Törəmə, Teylor, Sadə İnteqrallar)
        math_medium = [
            (r"24. Prove necessary and sufficient condition for differentiability ($f'(x_0)$ exists and is finite). (Theoretical)", "Medium"),
            (r"25. Prove the Product Rule: $(uv)^{\prime}=u^{\prime}v+uv^{\prime}$. (Theoretical)", "Medium"),
            (r"26. Differential of a function and its geometric meaning ($dy=f'(x)dx$). (Theoretical)", "Medium"),
            (r"27. Prove that differentiability implies continuity. (Theoretical)", "Medium"),
            (r"28. Find the derivative of $y(x)=(\sin 2x)^{x^{2}+1}$.", "Medium"),
            (r"29. Find the derivative of the implicit function $e^{y^{2}}=x^{x+2y}$.", "Medium"),
            (r"30. Find the 4th derivative of $y(x)=x^{2}\cos 2x$.", "Medium"),
            (r"31. Find the 10th derivative of $y(x)=\sin^{2}4x$.", "Medium"),
            (r"32. Rolle's Theorem (Theoretical).", "Medium"),
            (r"33. Lagrange's Mean Value Theorem (Theoretical).", "Medium"),
            (r"34. Cauchy's Mean Value Theorem (Theoretical).", "Medium"),
            (r"35. Calculate the limit $\lim_{x\rightarrow0}(\frac{\tan x}{x})^{1/x^{2}}$.", "Medium"),
            (r"36. Expand $f(x)=\sin x$ around $x_{0}=0$ using Taylor's formula.", "Medium"),
            (r"37. Expand $f(x)=\cos x$ around $x_{0}=0$ using Taylor's formula.", "Medium"),
            (r"38. Prove condition for differentiable function to increase is $f'(x) \ge 0$. (Theoretical)", "Medium"),
            (r"39. Determine the interval where $f(x)=\ln(1-x^{2})$ is increasing.", "Medium"),
            (r"40. Find the extrema of $f(x)=x-\ln(1+x)$.", "Medium"),
            (r"41. Find the extrema of $f(x)=\frac{x}{\ln x}$.", "Medium"),
            (r"42. Prove Fermat's Theorem: If extrema at $x_0$, then $f'(x_0)=0$ or doesn't exist. (Theoretical)", "Medium"),
            (r"43. Find the inflection point of $f(x)=e^{-x^{2}}+1$.", "Medium"),
            (r"44. Prove sufficient condition for inflection point ($f''(x)$ changes sign). (Theoretical)", "Medium"),
            (r"45. Find the asymptotes of $f(x)=\text{arcctg } x$.", "Medium"),
            (r"46. Find the asymptotes of $f(x)=\frac{2x^{2}-9}{x+2}$.", "Medium"),
            (r"47. Compute the integral $\int\frac{\sqrt{\ln x}}{2x}dx$.", "Medium"),
            (r"48. Compute the integral $\int x^{2}\sin 2x dx$.", "Medium"),
            (r"49. Compute the integral $\int \text{arcctg } x dx$.", "Medium"),
            (r"50. Compute the integral $\int\frac{x^{3}+3}{x^{2}-1}dx$.", "Medium"),
            (r"51. Compute the integral $\int\frac{3x^{2}+5}{x+1}dx$.", "Medium"),
            (r"52. Compute the integral $\int\frac{dx}{\sqrt{x^{2}+6x+10}}$.", "Medium"),
            (r"53. Compute the integral $\int\frac{1}{\sqrt{x}+\sqrt[3]{x}}dx$.", "Medium"),
            (r"54. Compute the integral \(\int\frac{dx}{x^{3}\sqrt{1+x^{2}}}\).", "Medium")
        ]

        # Hard Questions (Q55-Q75: İsbatlar, Qeyri-məxsusi inteqrallar, Çoxdəyişənli, Səth inteqralları)
        math_hard = [
            (r"55. Prove that a function \(f(x)\) which is integrable on \([a,b]\) is bounded on this interval. (Theoretical)", "Hard"),
            (r"56. Prove the Newton-Leibniz Formula: \(\int_{a}^{b}f(x)dx=F(b)-F(a)\). (Theoretical)", "Hard"),
            (r"57. Prove the Integration by Parts formula for definite integrals. (Theoretical)", "Hard"),
            (r"58. Evaluate the improper integral: \(\int_{0}^{+\infty}\frac{dx}{x^{2}+4}\).", "Hard"),
            (r"59. Evaluate the improper integral: \(\int_{-\infty}^{+\infty}\frac{dx}{x^{2}+16}\).", "Hard"),
            (r"60. Evaluate the improper integral: \(\int_{-\infty}^{+\infty}\frac{dx}{x^{2}+4x+13}\).", "Hard"),
            (r"61. Prove that the harmonic series \(\sum_{n=1}^{\infty}\frac{1}{n}\) is divergent. (Theoretical)", "Hard"),
            (r"62. Prove d'Alembert's Ratio Test (Theoretical).", "Hard"),
            (r"63. Investigate the convergence of the series \(\sum_{n=1}^{\infty}\frac{(-1)^{n}n}{n^{3}+4}\).", "Hard"),
            (r"64. Determine the interval of convergence of the power series \(\sum_{n=1}^{\infty}\frac{x^{n}}{n(n+3)}\).", "Hard"),
            (r"65. Investigate the continuity of the function \(f(x,y)=\frac{x-y}{x+y}\) at the point \(O(0,0)\).", "Hard"),
            (r"66. Find the directional derivative of \(f(x,y)=2y^{2}x+3x+4y+1\) at \(M(-1,1)\) in direction \(30^{\circ}\).", "Hard"),
            (r"67. Determine the extrema of the function \(f(x,y)=(y-x)^{2}+(y+2)^{2}\).", "Hard"),
            (r"68. Determine the extrema of \(f(x,y)=x+y\) subject to \(x^{2}+y^{2}=1\) (Lagrange Multipliers).", "Hard"),
            (r"69. Evaluate \(\iint_{D}(x+y^{3})dx dy\), if \(D=\{(x,y):1\le x\le2; 0\le y\le2\}\).", "Hard"),
            (r"70. If \(G\) is part of circle \(x^{2}+y^{2}=1\) in 1st quadrant, evaluate \(\iint_{G}e^{x^{2}+y^{2}}dx dy\).", "Hard"),
            (r"71. The change of variables formula in a triple integral (Jacobian). (Theoretical)", "Hard"),
            (r"72. If curve \(AB\) is arc of parabola \(y^{2}=2x\) from \((0,0)\) to \((2,2)\), compute \(\int_{AB}y dl\).", "Hard"),
            (r"73. If circle \(x^{2}+y^{2}=R^{2}\) is \(L\), compute \(\oint_{L}(x-y)dx+(x+y)dy\) (Green's Theorem).", "Hard"),
            (r"74. If curve \(AB\) is circle arc \(x=\cos t, y=\sin t\) in 2nd quadrant, compute \(\int_{AB}x^{2}dx+xy dy\).", "Hard"),
            (r"75. If \(S\) is part of surface \(x^{2}+y^{2}=1\) bounded by \(z=0, z=2\), evaluate \(\iint_{S}x dS\).", "Hard")
        ]

        # ==========================================
        # KOMPÜTER ARXİTEKTURASI SUALLARI
        # ==========================================
        arch_questions = [
            ("Explain input unit and associated peripherials", "Easy"),
            ("Explain output unit and associated peripherials", "Easy"),
            ("Explain differences between computer hardware and software", "Easy"),
            ("Explain primary storage unit", "Easy"),
            ("Explain componens of computer architecture", "Easy"),
            ("Give definition about operating system", "Easy"),
            ("Explain operating system types", "Easy"),
            ("Explain server operating system", "Easy"),
            ("Explain bios/uefi system", "Easy"),
            ("Explain output devices in computer system", "Easy"),
            ("Explain the basics of microchips", "Easy"),
            ("Explain benefits of personal computers", "Easy"),
            ("Explain personal computer disadvantages", "Easy"),
            ("Explain types of microprocessors", "Easy"),
            ("Explain features of microprocessor", "Easy"),
            ("Explain control unit", "Medium"),
            ("Explain register and arithmetic logic unit", "Medium"),
            ("Explain hexadecimal number system with examples", "Medium"),
            ("Write explanation about ASCII .", "Medium"),
            ("Convert 12B(16) numbering system to octal number system", "Medium"),
            ("Explain binary representation in microprocessors and CPUs", "Medium"),
            ("Explain Binary & Hexadecimal Representation in Memory (RAM, Hard Drives, SSDs)", "Medium"),
            ("Explain Binary & Hexadecimal Representation in Graphics Processing Units (GPUs)", "Medium"),
            ("Explain Binary, Decimal, and Hexadecimal Representation Networking Devices", "Medium"),
            ("Explain Devices and Efficiency of Number Representations", "Medium"),
            ("Explain Binary & Hexadecimal Representation Digital Displays (LED, LCD Screens)", "Medium"),
            ("Explain or , not logic gates and their truth tables", "Medium"),
            ("Explain xor , xnor logic gates and their truth tables", "Medium"),
            ("Explain nand logic gate truth tables", "Medium"),
            ("Explain logic gates definitions with truth tables", "Medium"),
            ("Explain and , nor logic gates and their truth tables", "Medium"),
            ("Convert 14D(16) numbering system to binary number system", "Medium"),
            ("Write about network operating system", "Medium"),
            ("Write basic cmd commands with definitions", "Medium"),
            ("Explain linux ls command with examples", "Medium"),
            ("Explain linux mkdir command with examples", "Medium"),
            ("Explain differences between GUI and CLI interfaces", "Medium"),
            ("Explain Binary Representation in Embedded Systems (Microcontrollers)", "Medium"),
            ("Explain binary number system and octal number system with examples", "Medium"),
            ("Explain virtual memory", "Medium"),
            ("Explain virtual memory advantages", "Medium"),
            ("Explain virtual memory disadvantages", "Medium"),
            ("Explain differences between physical and virtual memory", "Medium"),
            ("Explain monitoring virtual memory in linux", "Medium"),
            ("Explain cache memory", "Medium"),
            ("Explain cache memory levels", "Medium"),
            ("Explain cache memory techniques", "Medium"),
            ("Explain benefits of cache memory", "Medium"),
            ("Explain advantages and disadvantages of cache memory", "Medium"),
            ("Explain page cache, entry and inode cache mechanisms", "Medium"),
            ("Explain how to view cache in linux operating system", "Medium"),
            ("Why linux cache is very efficient?", "Medium"),
            ("Explain super user in Linux", "Medium"),
            ("Explain logging module with example", "Medium"),
            ("Explain using variables and input in bash shell script", "Medium"),
            ("Explain if else statements in bash shell script", "Medium"),
            ("Explain numeric comparisons operations in bash shell script", "Medium"),
            ("Explain string comparisons operations in bash shell script", "Medium"),
            ("Explain how to install linux distrubution in virtual machine", "Medium"),
            ("Explain RISC architecture", "Medium"),
            ("Explain CISC architecture", "Medium"),
            ("Explain instruction set architecture", "Medium"),
            ("Explain details about computer hardware security devices", "Medium"),
            ("Explain managing SELinux", "Medium"),
            ("Explain interaction of a program with hardware", "Medium"),
            ("Explain direct-mapped cache calculations", "Hard"),
            ("Consider a direct mapped cache of size 16 KB with block size 256 bytes. Main memory 128 KB. Find Tag bits & Tag directory size", "Hard"),
            ("Consider a direct mapped cache of size 512 KB with block size 1 KB. 7 tag bits. Find Size of main memory & Tag directory size.", "Hard"),
            ("Consider a direct mapped cache with block size 4 KB. Main memory 16 GB, 10 tag bits. Find Size of cache memory", "Hard"),
            ("Write the appropriate code that takes information about employees in txt format and extracts the email domains.", "Hard"),
            ("Write a code that extracts the address of the person who sent the most emails from a log file.", "Hard"),
            ("Explain add a new element (in array) in bash shell script", "Hard"),
            ("Write a program that computes the net amount of a bank account based a transaction log (D 100, W 200...)", "Hard"),
            ("Using def function display number of odd and even numbers Input: {'a': 1, 'b': 2...}", "Hard")
        ]

        # Add all questions to database
        try:
            # Math questions
            for q_text, difficulty in math_easy:
                db.session.add(Question(text=q_text, difficulty=difficulty, subject_id=subj_math.id))
            
            for q_text, difficulty in math_medium:
                db.session.add(Question(text=q_text, difficulty=difficulty, subject_id=subj_math.id))
            
            for q_text, difficulty in math_hard:
                db.session.add(Question(text=q_text, difficulty=difficulty, subject_id=subj_math.id))
            
            # Architecture questions
            for q_text, difficulty in arch_questions:
                db.session.add(Question(text=q_text, difficulty=difficulty, subject_id=subj_arch.id))

            db.session.commit()
            
            total_math = len(math_easy) + len(math_medium) + len(math_hard)
            print(f"Baza hazırdır! Riyazi Analiz: {total_math} sual, Arxitektura: {len(arch_questions)} sual.")
            
        except Exception as e:
            db.session.rollback()
            print(f"Xəta baş verdi: {e}")
            raise


if __name__ == "__main__":
    seed_database()