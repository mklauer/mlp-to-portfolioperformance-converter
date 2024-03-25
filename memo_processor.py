import re

# Regular expressions to find categories of transactions
depositRe = re.compile(r'LASTSCHRIFTEINR\.\n')
sellRe = re.compile(r'EFFEKTENGUTSCHRIFT\nWERTPAPIERABRECHNUNG\nVERKAUF')
sellOldRe = re.compile(r'EFFEKTENGUTSCHRIFT\nDEPOT.*\nWERTPAPIERABRECHNUNG')
taxRetRe = re.compile(r'EFFEKTENGUTSCHRIFT\nWERTPAPIERABRECHNUNG\nKAUF\nSTEUERAUSGLEICH')
dividendRe = re.compile(r'EFFEKTENGUTSCHRIFT\nWP-ERTR\S+GNISGUTSCHRIFT\nINVESTMENTFONDS')
buyRe = re.compile(r'EFFEKTEN\n')
collectRe = re.compile(r'EINZUGSERMAECHTIGUNG\n')
creditRe = re.compile(r'GUTSCHRIFT')
kirchTaxRe = re.compile(r'KIRCHENSTEUER\n')
soliTaxRe = re.compile(r'SOLIDARIT\S+TSZUSCHLAG\n')
kapiTaxRe = re.compile(r'KAPITALERTRAGSTEUER\n')
transRe = re.compile(r'UEBERWEISUNG\n')
entgeldRe = re.compile(r'ENTGELT\s')


class MemoProcessor:

    def __init__(self, memo, line_no):
        self.memo = memo
        self.line_no = line_no

    def process(self):
        # Determine output values that depend on the transaction type
        out_dict = {}
        transaction_is_valid = True
        if depositRe.match(self.memo) is not None:
            if self.memo.find('SPARPLAN') != -1:
                out_dict['Notiz'] = 'Sparplan'
            out_dict['Typ'] = 'Einlage'

        elif sellRe.match(self.memo) or sellOldRe.match(self.memo):
            pieces = self.find_pieces()
            if pieces == "":
                self.print_warning("Could not find number of pieces in line ")
                transaction_is_valid = False
            wkn = self.find_wkn()
            if wkn == "":
                self.print_warning("Could not find WKN in line ")
            # We can still use the transaction
            isin = self.find_isin()
            if isin == "":
                self.print_warning("Could not find ISIN in line ")
            # We can still use the transaction
            name = self.find_stock_name()
            if name == "":
                self.print_warning("Could not find the stock name in line ")
                transaction_is_valid = False
            taxes = self.find_taxes()
            if transaction_is_valid:
                out_dict['Typ'] = 'Verkauf'
                out_dict['Stück'] = pieces
                out_dict['WKN'] = wkn
                out_dict['ISIN'] = isin
                out_dict['Wertpapiername'] = name
                out_dict['Steuern'] = str(taxes).replace('.', ',')

        elif taxRetRe.match(self.memo) is not None:
            out_dict['Typ'] = 'Steuerrückerstattung'
            out_dict['Notiz'] = 'Steuerausgleich'
            out_dict['Stück'] = self.find_pieces()
            out_dict['WKN'] = self.find_wkn()
            out_dict['ISIN'] = self.find_isin()
            out_dict['Wertpapiername'] = self.find_stock_name()

        elif dividendRe.match(self.memo) is not None:
            out_dict['Typ'] = 'Steuerrückerstattung'
            out_dict['Notiz'] = 'Erträgnisgutschrift'

        elif buyRe.match(self.memo) is not None:
            pieces = self.find_pieces()
            if pieces == "":
                self.print_warning("Could not find number of pieces in line " + self.line_no)
                transaction_is_valid = False
            wkn = self.find_wkn()
            if wkn == "":
                self.print_warning("Could not find WKN in line " + self.line_no)
            # We can still use the transaction
            isin = self.find_isin()
            if isin == "":
                self.print_warning("Could not find ISIN in line " + self.line_no)
            # We can still use the transaction
            name = self.find_stock_name()
            if name == "":
                self.print_warning("Could not find the stock name in line ")
                transaction_is_valid = False
            if transaction_is_valid:
                out_dict['Typ'] = 'Kauf'
                out_dict['Stück'] = pieces
                out_dict['WKN'] = wkn
                out_dict['ISIN'] = isin
                out_dict['Wertpapiername'] = name

        elif (collectRe.match(self.memo) is not None) or entgeldRe.match(self.memo) is not None:
            if self.memo.find('DEPOTENTGELT') != -1:
                out_dict['Typ'] = 'Gebühren'
                out_dict['Notiz'] = 'Depotgebühr'
            else:
                out_dict['Typ'] = 'Entnahme'
                out_dict['Notiz'] = 'Unbekannte Abbuchung'

        elif creditRe.match(self.memo) is not None:
            if self.memo.find('VERTRIEBSFOLGEPROVISION') != -1:
                out_dict['Typ'] = 'Gebührenerstattung'
                out_dict['Notiz'] = 'Erstattung Vertriebsfolgeprovision'
            else:
                out_dict['Typ'] = 'Einlage'
                out_dict['Notiz'] = 'Unbekannte Gutschrift'

        elif kirchTaxRe.match(self.memo) is not None:
            out_dict['Typ'] = 'Steuern'
            out_dict['Notiz'] = 'Kirchensteuer'

        elif soliTaxRe.match(self.memo) is not None:
            out_dict['Typ'] = 'Steuern'
            out_dict['Notiz'] = 'Solidaritätszuschlag'

        elif kapiTaxRe.match(self.memo) is not None:
            out_dict['Typ'] = 'Steuern'
            out_dict['Notiz'] = 'Kapitalertragsteuer'

        elif transRe.match(self.memo):
            out_dict['Typ'] = 'Entnahme'

        return out_dict

    def find_pieces(self):
        """Find the number of traded stock pieces in a transaction text

        Returns the number of pieces as a string if the number was found and an
        empty string otherwise
        """
        regex = r'MENGE\s+(\d+,?\d*)'
        matches = re.search(regex, self.memo)
        if matches:
            return matches.group(1)
        else:
            return ""

    def print_warning(self, text):
        """Print an orange colored warning text to stdout"""
        print('\033[33mWarning: ' + text + self.line_no + '\033[0m')

    def find_wkn(self):
        """Find the WKN in a transaction text

        Returns the WKN if it was found and an empty string otherwise
        """
        regex = r'WKN (.*) /'
        matches = re.search(regex, self.memo)
        if matches:
            return matches.group(1)
        else:
            return ""

    def find_isin(self):
        """Find the ISIN in a transaction text

        Returns the ISIN if it was found and an empty string otherwise
        """
        regex = r'WKN.*/ ([0-9a-zA-Z]*)'
        matches = re.search(regex, self.memo)
        if matches:
            return matches.group(1)
        else:
            return ""

    def find_stock_name(self):
        """Find and translate the stock name in a transaction text

        Returns the stock name if it was found and an empty string otherwise. The
        stock name is translated to a more readable string if the abbreviated
        version is known. If it is unknown, the abbreviated string is returned.
        """
        # Dictionary mapping abbreviated stock names to full stock names
        stock_dict = {
            'ACATIS-GANE VAL.EV.F.UI A': 'Acatis Gané Value Event Fonds',
            'ISHS CORE DAX UCITS ETF': 'iShares Core DAX UCITS ETF',
            'ISHSIII-CORE MSCI WLD DLA': 'iShares Core MSCI World UCITS ETF',
            'CARMIGN.PATRIMOI. AEO ACC': 'Carmignac Patrimoine A',
            'THREADN.INV.-EU.S.C. RAEO': 'Threadneedle European Smaller Companies',
            'ETHNA-DEFENSIV INH. T': 'Ethna-Defensiv T EUR ACC'
        }

        regex = r'WKN.*\n(.*)\n'
        matches = re.search(regex, self.memo)
        if matches:
            name = matches.group(1)
            # The structure of the transaction has changed over time: the stock name
            # used to be in the line before the WKN but is now in the line after the
            # WKN. If the name contains "HANDELSTAG" we assume that we have an old
            # transcation text.
            if name.find('HANDELSTAG') != -1:
                # Old transaction text. We have to look before the WKN
                regex = r'(.*)\nWKN.*/.*\n'
                matches = re.search(regex, self.memo)
                if matches:
                    name = matches.group(1)
                else:
                    return ""
        else:
            return ""

        # Try to translate the abbreviated name
        if name in stock_dict:
            return stock_dict[name]
        else:
            return name

    def find_taxes(self):
        """Find tax amount in a transaction text

        Looks for tax substractions and returns the total amount of taxes if there
        are any, and 0 otherwise.
        """
        kap = 0
        kap_regex = r'KAPST\s+(.*)-'
        matches = re.search(kap_regex, self.memo)
        if matches:
            kap_str = matches.group(1)
            kap = float(kap_str.replace(',', '.'))

        soli = 0
        soli_regex = r'SOLZ\s+(.*)-'
        matches = re.search(soli_regex, self.memo)
        if matches:
            soli_str = matches.group(1)
            soli = float(soli_str.replace(',', '.'))

        kist = 0
        kist_regex = r'KIST\s+(.*)-'
        matches = re.search(kist_regex, self.memo)
        if matches:
            kist_str = matches.group(1)
            kist = float(kist_str.replace(',', '.'))

        return kap + soli + kist
